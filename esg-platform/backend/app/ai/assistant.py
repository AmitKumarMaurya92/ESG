"""
ESG AI Assistant service.

Uses RAG: retrieve organization context first, then ask the LLM.
The LLM NEVER invents company data, emission factors, or compliance requirements.
"""

import logging
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.ai.provider import get_ai_provider
from app.models.emission import Scope1Record, Scope2Record, Scope3Record
from app.models.esg import ESGMetric, ESGScore
from app.models.compliance import ComplianceRecord, FrameworkRequirement, Framework
from app.models.facility import Facility
from app.models.document import Document
from app.models.risk import RiskEvent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an ESG AI Assistant for the ESG Intelligence & Carbon Accounting Platform.

CRITICAL RULES:
1. You MUST only answer questions using the organization data provided below.
2. You MUST NOT invent emission factors, carbon calculations, or regulatory requirements.
3. You MUST NOT fabricate company-specific data.
4. If the data does not contain enough information to answer, say: "I don't have sufficient data in the current records to answer this question."
5. Always cite the data source (e.g., "Based on your Scope 2 records for 2026-07...").
6. Be concise, professional, and data-driven.
7. Use metric units (tCO2e, kWh, etc.) consistently.

Your role:
- Explain what the data shows
- Identify trends and anomalies
- Highlight compliance gaps
- Summarize ESG performance
- Answer methodology questions using standard GHG Protocol / GRI principles

You are NOT a general-purpose chatbot. Focus exclusively on ESG topics using the provided data.
"""


async def build_organization_context(
    db: AsyncSession,
    organization_id: uuid.UUID,
) -> str:
    """
    Build a concise text context from the organization's actual data.
    This is the retrieval step in RAG.
    """
    context_parts = []

    # ── Emissions Summary ──────────────────────────────────────────────────────
    scope1_result = await db.execute(
        select(func.sum(Scope1Record.co2e), func.count(Scope1Record.id))
        .where(Scope1Record.organization_id == organization_id)
    )
    s1_sum, s1_count = scope1_result.one()

    scope2_result = await db.execute(
        select(func.sum(Scope2Record.co2e), func.count(Scope2Record.id))
        .where(Scope2Record.organization_id == organization_id)
    )
    s2_sum, s2_count = scope2_result.one()

    scope3_result = await db.execute(
        select(func.sum(Scope3Record.co2e), func.count(Scope3Record.id))
        .where(Scope3Record.organization_id == organization_id)
    )
    s3_sum, s3_count = scope3_result.one()

    total_co2e = (s1_sum or 0) + (s2_sum or 0) + (s3_sum or 0)
    context_parts.append(f"""## Emissions Summary
- Total CO2e: {total_co2e:.2f} kgCO2e
- Scope 1 (direct): {s1_sum or 0:.2f} kgCO2e ({s1_count or 0} records)
- Scope 2 (purchased energy): {s2_sum or 0:.2f} kgCO2e ({s2_count or 0} records)
- Scope 3 (value chain): {s3_sum or 0:.2f} kgCO2e ({s3_count or 0} records)
""")

    # ── Recent Scope 2 Records ─────────────────────────────────────────────────
    s2_records_result = await db.execute(
        select(Scope2Record)
        .where(Scope2Record.organization_id == organization_id)
        .order_by(Scope2Record.created_at.desc())
        .limit(5)
    )
    s2_records = s2_records_result.scalars().all()
    if s2_records:
        s2_lines = [f"  - {r.period}: {r.activity_value} {r.activity_unit} ({r.category}) → {r.co2e:.2f} kgCO2e" for r in s2_records]
        context_parts.append("## Recent Scope 2 Records\n" + "\n".join(s2_lines) + "\n")

    # ── ESG Score ─────────────────────────────────────────────────────────────
    score_result = await db.execute(
        select(ESGScore)
        .where(ESGScore.organization_id == organization_id)
        .order_by(ESGScore.created_at.desc())
        .limit(1)
    )
    score = score_result.scalars().first()
    if score:
        context_parts.append(f"""## Latest ESG Score (Period: {score.period})
- Overall: {score.overall_score}
- Environmental: {score.environmental_score}
- Social: {score.social_score}
- Governance: {score.governance_score}
- Methodology: {score.methodology_version}
""")

    # ── Compliance Status ─────────────────────────────────────────────────────
    compliance_result = await db.execute(
        select(ComplianceRecord, FrameworkRequirement, Framework)
        .join(FrameworkRequirement, ComplianceRecord.requirement_id == FrameworkRequirement.id)
        .join(Framework, FrameworkRequirement.framework_id == Framework.id)
        .where(ComplianceRecord.organization_id == organization_id)
        .order_by(ComplianceRecord.updated_at.desc())
        .limit(20)
    )
    compliance_rows = compliance_result.all()
    if compliance_rows:
        compliance_lines = []
        for cr, req, fw in compliance_rows:
            compliance_lines.append(f"  - [{fw.name} {fw.version}] {req.requirement_code} '{req.title}': {cr.status}")
        context_parts.append("## Compliance Status\n" + "\n".join(compliance_lines) + "\n")

    # ── Open Risks ────────────────────────────────────────────────────────────
    risk_result = await db.execute(
        select(RiskEvent)
        .where(
            RiskEvent.organization_id == organization_id,
            RiskEvent.status == "open",
        )
        .order_by(RiskEvent.created_at.desc())
        .limit(10)
    )
    risks = risk_result.scalars().all()
    if risks:
        risk_lines = [f"  - [{r.severity}] {r.metric}: actual={r.actual_value}, expected≈{r.expected_value}" for r in risks]
        context_parts.append("## Open Risk Events\n" + "\n".join(risk_lines) + "\n")

    # ── Facilities ────────────────────────────────────────────────────────────
    fac_result = await db.execute(
        select(Facility).where(Facility.organization_id == organization_id)
    )
    facilities = fac_result.scalars().all()
    if facilities:
        fac_lines = [f"  - {f.name} ({f.facility_type}, {f.country})" for f in facilities]
        context_parts.append("## Facilities\n" + "\n".join(fac_lines) + "\n")

    if not context_parts:
        return "No data has been entered for this organization yet."

    return "\n".join(context_parts)


async def chat_with_assistant(
    db: AsyncSession,
    organization_id: uuid.UUID,
    user_message: str,
) -> tuple[str, list[str]]:
    """
    Main chat function. Returns (response_text, source_citations).
    
    Workflow:
    1. Retrieve organization context (RAG retrieval)
    2. Build prompt with context
    3. Call LLM
    4. Return response with sources
    """
    # Step 1: Retrieve context
    context = await build_organization_context(db, organization_id)

    # Step 2: Build prompt
    prompt = f"""## Organization Data Context
{context}

---

## User Question
{user_message}

Please answer using only the data provided above. If a definitive answer requires data that isn't shown, say so clearly.
"""

    # Step 3: Call LLM
    provider = get_ai_provider()
    try:
        response = await provider.generate(
            prompt=prompt,
            system=SYSTEM_PROMPT,
            max_tokens=1024,
        )
    except Exception as e:
        logger.error("AI provider error: %s", e)
        response = (
            "I encountered an error while processing your request. "
            "Please check that your LLM_API_KEY is configured correctly."
        )

    # Step 4: Build source citations from context sections
    sources = []
    if "Emissions Summary" in context:
        sources.append("Emissions Database")
    if "Recent Scope 2 Records" in context:
        sources.append("Scope 2 Records")
    if "ESG Score" in context:
        sources.append("ESG Score Engine")
    if "Compliance Status" in context:
        sources.append("Compliance Records")
    if "Open Risk Events" in context:
        sources.append("Risk Engine")
    if "Facilities" in context:
        sources.append("Facility Registry")

    if not sources:
        sources = ["No data available"]

    return response, sources
