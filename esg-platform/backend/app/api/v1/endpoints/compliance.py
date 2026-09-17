"""
Compliance API endpoints.

Manages framework requirements and per-organization compliance records.
"""

import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from datetime import datetime

from app.api import deps
from app.db.session import get_db
from app.models.compliance import Framework, FrameworkRequirement, ComplianceRecord

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class FrameworkOut(BaseModel):
    id: uuid.UUID
    name: str
    version: str
    description: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}


class RequirementOut(BaseModel):
    id: uuid.UUID
    framework_id: uuid.UUID
    requirement_code: str
    title: str
    description: Optional[str]
    required_data: Optional[str]
    applicability: Optional[str]
    source: Optional[str]
    model_config = {"from_attributes": True}


class ComplianceRecordOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    requirement_id: uuid.UUID
    status: str
    notes: Optional[str]
    updated_at: datetime
    # Joined fields
    requirement_code: Optional[str] = None
    requirement_title: Optional[str] = None
    framework_name: Optional[str] = None
    framework_version: Optional[str] = None
    model_config = {"from_attributes": True}


class ComplianceStatusUpdate(BaseModel):
    status: str  # COMPLETE, PARTIAL, MISSING, NEEDS_REVIEW, NOT_APPLICABLE
    notes: Optional[str] = None
    evidence_document_id: Optional[uuid.UUID] = None


class ComplianceMatrix(BaseModel):
    framework: str
    version: str
    total: int
    complete: int
    partial: int
    missing: int
    needs_review: int
    not_applicable: int
    compliance_pct: float
    requirements: List[ComplianceRecordOut]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/frameworks", response_model=List[FrameworkOut],
            summary="List all available compliance frameworks")
async def list_frameworks(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(select(Framework).order_by(Framework.name))
    return result.scalars().all()


@router.get("/frameworks/{framework_id}/requirements", response_model=List[RequirementOut],
            summary="List requirements for a specific framework")
async def list_requirements(
    framework_id: uuid.UUID,
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(FrameworkRequirement)
        .where(FrameworkRequirement.framework_id == framework_id)
        .order_by(FrameworkRequirement.requirement_code)
    )
    return result.scalars().all()


@router.get("/matrix", response_model=List[ComplianceMatrix],
            summary="Compliance matrix for all frameworks")
async def get_compliance_matrix(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    org_uuid = uuid.UUID(org_id)

    # Get all frameworks
    fw_result = await db.execute(select(Framework))
    frameworks = fw_result.scalars().all()

    matrix = []
    for fw in frameworks:
        # Get all requirements for this framework
        req_result = await db.execute(
            select(FrameworkRequirement)
            .where(FrameworkRequirement.framework_id == fw.id)
        )
        requirements = req_result.scalars().all()
        req_map = {r.id: r for r in requirements}

        # Get compliance records for this org
        cr_result = await db.execute(
            select(ComplianceRecord)
            .where(
                ComplianceRecord.organization_id == org_uuid,
                ComplianceRecord.requirement_id.in_(list(req_map.keys())),
            )
        )
        crs = cr_result.scalars().all()
        cr_map = {cr.requirement_id: cr for cr in crs}

        # Count statuses
        statuses = {"COMPLETE": 0, "PARTIAL": 0, "MISSING": 0, "NEEDS_REVIEW": 0, "NOT_APPLICABLE": 0}
        records_out = []

        for req in requirements:
            cr = cr_map.get(req.id)
            st = cr.status if cr else "MISSING"
            statuses[st] = statuses.get(st, 0) + 1
            records_out.append(ComplianceRecordOut(
                id=cr.id if cr else uuid.uuid4(),
                organization_id=org_uuid,
                requirement_id=req.id,
                status=st,
                notes=cr.notes if cr else None,
                updated_at=cr.updated_at if cr else datetime.utcnow(),
                requirement_code=req.requirement_code,
                requirement_title=req.title,
                framework_name=fw.name,
                framework_version=fw.version,
            ))

        total = len(requirements)
        complete = statuses.get("COMPLETE", 0)
        pct = round((complete / total * 100), 1) if total > 0 else 0.0

        matrix.append(ComplianceMatrix(
            framework=fw.name,
            version=fw.version,
            total=total,
            complete=complete,
            partial=statuses.get("PARTIAL", 0),
            missing=statuses.get("MISSING", 0),
            needs_review=statuses.get("NEEDS_REVIEW", 0),
            not_applicable=statuses.get("NOT_APPLICABLE", 0),
            compliance_pct=pct,
            requirements=records_out,
        ))

    return matrix


@router.patch("/records/{requirement_id}", response_model=ComplianceRecordOut,
              summary="Update compliance status for a requirement")
async def update_compliance_status(
    requirement_id: uuid.UUID,
    update: ComplianceStatusUpdate,
    current_user=Depends(deps.get_current_user),
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    org_uuid = uuid.UUID(org_id)

    valid_statuses = {"COMPLETE", "PARTIAL", "MISSING", "NEEDS_REVIEW", "NOT_APPLICABLE"}
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    # Verify requirement exists
    req_result = await db.execute(
        select(FrameworkRequirement).where(FrameworkRequirement.id == requirement_id)
    )
    req = req_result.scalars().first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")

    # Upsert compliance record
    cr_result = await db.execute(
        select(ComplianceRecord).where(
            ComplianceRecord.organization_id == org_uuid,
            ComplianceRecord.requirement_id == requirement_id,
        )
    )
    cr = cr_result.scalars().first()

    if cr:
        cr.status = update.status
        cr.notes = update.notes
        if update.evidence_document_id:
            cr.evidence_document_id = update.evidence_document_id
    else:
        cr = ComplianceRecord(
            organization_id=org_uuid,
            requirement_id=requirement_id,
            status=update.status,
            notes=update.notes,
            evidence_document_id=update.evidence_document_id,
        )
        db.add(cr)

    await db.commit()
    await db.refresh(cr)

    # Get framework for response
    fw_result = await db.execute(
        select(Framework).where(Framework.id == req.framework_id)
    )
    fw = fw_result.scalars().first()

    return ComplianceRecordOut(
        id=cr.id,
        organization_id=cr.organization_id,
        requirement_id=cr.requirement_id,
        status=cr.status,
        notes=cr.notes,
        updated_at=cr.updated_at,
        requirement_code=req.requirement_code,
        requirement_title=req.title,
        framework_name=fw.name if fw else None,
        framework_version=fw.version if fw else None,
    )
