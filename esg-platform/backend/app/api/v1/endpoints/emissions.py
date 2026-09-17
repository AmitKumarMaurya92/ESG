"""
Emissions API endpoints — Scope 1, 2, and 3.

Uses the deterministic carbon calculation engine (app.carbon.calculator).
LLMs are NEVER used for emission calculations.
"""

import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.api import deps
from app.db.session import get_db
from app.models.emission import Scope1Record, Scope2Record, Scope3Record
from app.carbon.calculator import calculate_co2e
from app.services.audit import log_action
from pydantic import BaseModel, field_validator
from datetime import datetime

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class ScopeBase(BaseModel):
    facility_id: uuid.UUID
    category: str
    activity_value: float
    activity_unit: str
    period: str  # e.g. "2026-07"

    @field_validator("activity_value")
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("activity_value must be greater than zero")
        return v


class Scope1Create(ScopeBase):
    source_document_id: Optional[uuid.UUID] = None


class Scope2Create(ScopeBase):
    calculation_method: str = "location-based"
    source_document_id: Optional[uuid.UUID] = None


class Scope3Create(ScopeBase):
    sub_category: Optional[str] = None
    source_document_id: Optional[uuid.UUID] = None


class ScopeResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    facility_id: uuid.UUID
    category: str
    activity_value: float
    activity_unit: str
    period: str
    co2e: float
    emission_factor_id: Optional[uuid.UUID]
    created_at: datetime
    model_config = {"from_attributes": True}


class EmissionsSummary(BaseModel):
    total_co2e: float
    scope1_co2e: float
    scope2_co2e: float
    scope3_co2e: float
    scope1_count: int
    scope2_count: int
    scope3_count: int


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _do_calculation(db, scope, category, activity_value, activity_unit, calculation_method="standard"):
    result = await calculate_co2e(
        db=db,
        scope=scope,
        category=category,
        activity_value=activity_value,
        activity_unit=activity_unit,
        calculation_method=calculation_method,
    )
    return result


# ── Scope 1 Endpoints ─────────────────────────────────────────────────────────

@router.post("/scope1", response_model=ScopeResponse, status_code=status.HTTP_201_CREATED,
             summary="Record a Scope 1 (direct) emission",
             description="Creates a Scope 1 emission record. CO2e is calculated deterministically using the emission factor database.")
async def create_scope1(
    record_in: Scope1Create,
    current_user=Depends(deps.get_current_user),
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    calc = await _do_calculation(db, 1, record_in.category, record_in.activity_value, record_in.activity_unit)

    record = Scope1Record(
        facility_id=record_in.facility_id,
        category=record_in.category,
        activity_value=record_in.activity_value,
        activity_unit=record_in.activity_unit,
        period=record_in.period,
        source_document_id=record_in.source_document_id,
        organization_id=uuid.UUID(org_id),
        co2e=calc.co2e_kg,
        emission_factor_id=calc.emission_factor_id,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    await log_action(
        db, current_user.id, uuid.UUID(org_id),
        "CREATE", "scope1_record", record.id,
        new_value=f"{record.co2e:.2f} kgCO2e for {record.activity_value} {record.activity_unit}",
    )

    return record


@router.get("/scope1", response_model=List[ScopeResponse],
            summary="List Scope 1 records for the current organization")
async def list_scope1(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
    period: Optional[str] = None,
) -> Any:
    stmt = select(Scope1Record).where(Scope1Record.organization_id == uuid.UUID(org_id))
    if period:
        stmt = stmt.where(Scope1Record.period == period)
    stmt = stmt.order_by(Scope1Record.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


# ── Scope 2 Endpoints ─────────────────────────────────────────────────────────

@router.post("/scope2", response_model=ScopeResponse, status_code=status.HTTP_201_CREATED,
             summary="Record a Scope 2 (purchased energy) emission")
async def create_scope2(
    record_in: Scope2Create,
    current_user=Depends(deps.get_current_user),
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    calc = await _do_calculation(
        db, 2, record_in.category,
        record_in.activity_value, record_in.activity_unit,
        record_in.calculation_method,
    )

    record = Scope2Record(
        facility_id=record_in.facility_id,
        category=record_in.category,
        activity_value=record_in.activity_value,
        activity_unit=record_in.activity_unit,
        period=record_in.period,
        calculation_method=record_in.calculation_method,
        source_document_id=record_in.source_document_id,
        organization_id=uuid.UUID(org_id),
        co2e=calc.co2e_kg,
        emission_factor_id=calc.emission_factor_id,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    await log_action(
        db, current_user.id, uuid.UUID(org_id),
        "CREATE", "scope2_record", record.id,
        new_value=f"{record.co2e:.2f} kgCO2e for {record.activity_value} {record.activity_unit}",
    )

    return record


@router.get("/scope2", response_model=List[ScopeResponse],
            summary="List Scope 2 records for the current organization")
async def list_scope2(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
    period: Optional[str] = None,
) -> Any:
    stmt = select(Scope2Record).where(Scope2Record.organization_id == uuid.UUID(org_id))
    if period:
        stmt = stmt.where(Scope2Record.period == period)
    stmt = stmt.order_by(Scope2Record.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


# ── Scope 3 Endpoints ─────────────────────────────────────────────────────────

@router.post("/scope3", response_model=ScopeResponse, status_code=status.HTTP_201_CREATED,
             summary="Record a Scope 3 (value chain) emission")
async def create_scope3(
    record_in: Scope3Create,
    current_user=Depends(deps.get_current_user),
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    calc = await _do_calculation(db, 3, record_in.category, record_in.activity_value, record_in.activity_unit)

    record = Scope3Record(
        facility_id=record_in.facility_id,
        category=record_in.category,
        sub_category=record_in.sub_category,
        activity_value=record_in.activity_value,
        activity_unit=record_in.activity_unit,
        period=record_in.period,
        source_document_id=record_in.source_document_id,
        organization_id=uuid.UUID(org_id),
        co2e=calc.co2e_kg,
        emission_factor_id=calc.emission_factor_id,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    await log_action(
        db, current_user.id, uuid.UUID(org_id),
        "CREATE", "scope3_record", record.id,
        new_value=f"{record.co2e:.2f} kgCO2e for {record.activity_value} {record.activity_unit}",
    )

    return record


@router.get("/scope3", response_model=List[ScopeResponse],
            summary="List Scope 3 records for the current organization")
async def list_scope3(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
    period: Optional[str] = None,
) -> Any:
    stmt = select(Scope3Record).where(Scope3Record.organization_id == uuid.UUID(org_id))
    if period:
        stmt = stmt.where(Scope3Record.period == period)
    stmt = stmt.order_by(Scope3Record.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


# ── Summary Endpoint ──────────────────────────────────────────────────────────

@router.get("/summary", response_model=EmissionsSummary,
            summary="Get emissions summary for the current organization")
async def get_emissions_summary(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    org_uuid = uuid.UUID(org_id)

    s1 = await db.execute(
        select(func.sum(Scope1Record.co2e), func.count(Scope1Record.id))
        .where(Scope1Record.organization_id == org_uuid)
    )
    s1_sum, s1_count = s1.one()

    s2 = await db.execute(
        select(func.sum(Scope2Record.co2e), func.count(Scope2Record.id))
        .where(Scope2Record.organization_id == org_uuid)
    )
    s2_sum, s2_count = s2.one()

    s3 = await db.execute(
        select(func.sum(Scope3Record.co2e), func.count(Scope3Record.id))
        .where(Scope3Record.organization_id == org_uuid)
    )
    s3_sum, s3_count = s3.one()

    s1_val = float(s1_sum or 0)
    s2_val = float(s2_sum or 0)
    s3_val = float(s3_sum or 0)

    return EmissionsSummary(
        total_co2e=s1_val + s2_val + s3_val,
        scope1_co2e=s1_val,
        scope2_co2e=s2_val,
        scope3_co2e=s3_val,
        scope1_count=int(s1_count or 0),
        scope2_count=int(s2_count or 0),
        scope3_count=int(s3_count or 0),
    )
