"""
Analytics API — aggregated data for dashboards.

Returns chart-ready data for Recharts.
Queries run against verified database records only.
"""

import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, text
from pydantic import BaseModel
from datetime import datetime

from app.api import deps
from app.db.session import get_db
from app.models.emission import Scope1Record, Scope2Record, Scope3Record
from app.models.esg import ESGScore, ESGMetric
from app.models.risk import RiskEvent
from app.models.compliance import ComplianceRecord, Framework, FrameworkRequirement
from app.models.document import Document
from app.models.facility import Facility

router = APIRouter()


# ── Response schemas ──────────────────────────────────────────────────────────

class DashboardSummary(BaseModel):
    total_co2e: float
    scope1_co2e: float
    scope2_co2e: float
    scope3_co2e: float
    esg_score: Optional[float]
    environmental_score: Optional[float]
    social_score: Optional[float]
    governance_score: Optional[float]
    open_risks: int
    documents_count: int
    facilities_count: int
    compliance_pct: Optional[float]


class EmissionsChartPoint(BaseModel):
    period: str
    scope1: float
    scope2: float
    scope3: float
    total: float


class ScopeDistribution(BaseModel):
    name: str
    value: float
    color: str


class FacilityEmissions(BaseModel):
    facility_id: str
    facility_name: str
    co2e: float


class CategoryEmissions(BaseModel):
    category: str
    scope: int
    co2e: float


class RiskSummary(BaseModel):
    total: int
    critical: int
    high: int
    medium: int
    low: int


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/summary", response_model=DashboardSummary,
            summary="Main dashboard summary card data")
async def get_dashboard_summary(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    org_uuid = uuid.UUID(org_id)

    # Emissions aggregation
    s1 = await db.execute(select(func.sum(Scope1Record.co2e)).where(Scope1Record.organization_id == org_uuid))
    s2 = await db.execute(select(func.sum(Scope2Record.co2e)).where(Scope2Record.organization_id == org_uuid))
    s3 = await db.execute(select(func.sum(Scope3Record.co2e)).where(Scope3Record.organization_id == org_uuid))

    s1_val = float(s1.scalar() or 0)
    s2_val = float(s2.scalar() or 0)
    s3_val = float(s3.scalar() or 0)

    # Latest ESG score
    score_result = await db.execute(
        select(ESGScore)
        .where(ESGScore.organization_id == org_uuid)
        .order_by(ESGScore.created_at.desc())
        .limit(1)
    )
    score = score_result.scalars().first()

    # Open risks
    risk_result = await db.execute(
        select(func.count(RiskEvent.id))
        .where(RiskEvent.organization_id == org_uuid, RiskEvent.status == "open")
    )
    open_risks = int(risk_result.scalar() or 0)

    # Document count
    doc_result = await db.execute(
        select(func.count(Document.id)).where(Document.organization_id == org_uuid)
    )
    docs_count = int(doc_result.scalar() or 0)

    # Facility count
    fac_result = await db.execute(
        select(func.count(Facility.id)).where(Facility.organization_id == org_uuid)
    )
    fac_count = int(fac_result.scalar() or 0)

    # Compliance %
    compliance_pct = None
    total_cr = await db.execute(
        select(func.count(ComplianceRecord.id))
        .where(ComplianceRecord.organization_id == org_uuid)
    )
    total_count = int(total_cr.scalar() or 0)
    if total_count > 0:
        complete_cr = await db.execute(
            select(func.count(ComplianceRecord.id))
            .where(
                ComplianceRecord.organization_id == org_uuid,
                ComplianceRecord.status == "COMPLETE",
            )
        )
        complete_count = int(complete_cr.scalar() or 0)
        compliance_pct = round((complete_count / total_count) * 100, 1)

    return DashboardSummary(
        total_co2e=round(s1_val + s2_val + s3_val, 2),
        scope1_co2e=round(s1_val, 2),
        scope2_co2e=round(s2_val, 2),
        scope3_co2e=round(s3_val, 2),
        esg_score=score.overall_score if score else None,
        environmental_score=score.environmental_score if score else None,
        social_score=score.social_score if score else None,
        governance_score=score.governance_score if score else None,
        open_risks=open_risks,
        documents_count=docs_count,
        facilities_count=fac_count,
        compliance_pct=compliance_pct,
    )


@router.get("/emissions/trend", response_model=List[EmissionsChartPoint],
            summary="Emissions over time (by period) for trend charts")
async def get_emissions_trend(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    org_uuid = uuid.UUID(org_id)

    # Aggregate by period
    async def agg_by_period(Model):
        result = await db.execute(
            select(Model.period, func.sum(Model.co2e).label("total"))
            .where(Model.organization_id == org_uuid)
            .group_by(Model.period)
            .order_by(Model.period)
        )
        return {row.period: float(row.total) for row in result.all()}

    s1_map = await agg_by_period(Scope1Record)
    s2_map = await agg_by_period(Scope2Record)
    s3_map = await agg_by_period(Scope3Record)

    # Union of all periods
    all_periods = sorted(set(list(s1_map.keys()) + list(s2_map.keys()) + list(s3_map.keys())))

    points = []
    for period in all_periods:
        s1 = s1_map.get(period, 0.0)
        s2 = s2_map.get(period, 0.0)
        s3 = s3_map.get(period, 0.0)
        points.append(EmissionsChartPoint(
            period=period,
            scope1=round(s1, 2),
            scope2=round(s2, 2),
            scope3=round(s3, 2),
            total=round(s1 + s2 + s3, 2),
        ))

    return points


@router.get("/emissions/scope-distribution", response_model=List[ScopeDistribution],
            summary="Scope 1/2/3 distribution for pie chart")
async def get_scope_distribution(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    org_uuid = uuid.UUID(org_id)

    s1 = float((await db.execute(select(func.sum(Scope1Record.co2e)).where(Scope1Record.organization_id == org_uuid))).scalar() or 0)
    s2 = float((await db.execute(select(func.sum(Scope2Record.co2e)).where(Scope2Record.organization_id == org_uuid))).scalar() or 0)
    s3 = float((await db.execute(select(func.sum(Scope3Record.co2e)).where(Scope3Record.organization_id == org_uuid))).scalar() or 0)

    return [
        ScopeDistribution(name="Scope 1", value=round(s1, 2), color="#10b981"),
        ScopeDistribution(name="Scope 2", value=round(s2, 2), color="#3b82f6"),
        ScopeDistribution(name="Scope 3", value=round(s3, 2), color="#f59e0b"),
    ]


@router.get("/emissions/by-facility", response_model=List[FacilityEmissions],
            summary="Emissions broken down by facility")
async def get_emissions_by_facility(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    org_uuid = uuid.UUID(org_id)

    # Get all facilities
    fac_result = await db.execute(
        select(Facility).where(Facility.organization_id == org_uuid)
    )
    facilities = {str(f.id): f.name for f in fac_result.scalars().all()}

    # Aggregate scope 1+2 by facility
    agg: dict[str, float] = {fid: 0.0 for fid in facilities}

    for Model in [Scope1Record, Scope2Record, Scope3Record]:
        result = await db.execute(
            select(Model.facility_id, func.sum(Model.co2e).label("total"))
            .where(Model.organization_id == org_uuid)
            .group_by(Model.facility_id)
        )
        for row in result.all():
            fid = str(row.facility_id)
            if fid in agg:
                agg[fid] += float(row.total or 0)

    return [
        FacilityEmissions(
            facility_id=fid,
            facility_name=facilities[fid],
            co2e=round(co2e, 2),
        )
        for fid, co2e in agg.items()
    ]


@router.get("/emissions/by-category", response_model=List[CategoryEmissions],
            summary="Emissions broken down by category and scope")
async def get_emissions_by_category(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    org_uuid = uuid.UUID(org_id)
    results = []

    for scope, Model in [(1, Scope1Record), (2, Scope2Record), (3, Scope3Record)]:
        agg = await db.execute(
            select(Model.category, func.sum(Model.co2e).label("total"))
            .where(Model.organization_id == org_uuid)
            .group_by(Model.category)
            .order_by(func.sum(Model.co2e).desc())
        )
        for row in agg.all():
            results.append(CategoryEmissions(
                category=row.category,
                scope=scope,
                co2e=round(float(row.total or 0), 2),
            ))

    return results


@router.get("/risks/summary", response_model=RiskSummary,
            summary="Risk event counts by severity")
async def get_risk_summary(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    org_uuid = uuid.UUID(org_id)

    async def count_by_severity(severity: str) -> int:
        result = await db.execute(
            select(func.count(RiskEvent.id))
            .where(
                RiskEvent.organization_id == org_uuid,
                RiskEvent.severity == severity,
                RiskEvent.status == "open",
            )
        )
        return int(result.scalar() or 0)

    total = await db.execute(
        select(func.count(RiskEvent.id))
        .where(RiskEvent.organization_id == org_uuid, RiskEvent.status == "open")
    )

    return RiskSummary(
        total=int(total.scalar() or 0),
        critical=await count_by_severity("CRITICAL"),
        high=await count_by_severity("HIGH"),
        medium=await count_by_severity("MEDIUM"),
        low=await count_by_severity("LOW"),
    )
