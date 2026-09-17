"""
ESG Metrics & Scoring endpoints.

Records ESG metrics and calculates transparent ESG scores.
Scoring is done by the deterministic engine, not an LLM.
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
from app.models.esg import ESGMetric, ESGScore
from app.carbon.scoring import calculate_esg_score, save_esg_score

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class ESGMetricCreate(BaseModel):
    category: str        # Environmental, Social, Governance
    name: str
    value: float
    unit: str
    period: str          # e.g. "2026-07"


class ESGMetricOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    category: str
    name: str
    value: float
    unit: str
    period: str
    created_at: datetime
    model_config = {"from_attributes": True}


class ESGScoreOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    period: str
    overall_score: float
    environmental_score: float
    social_score: float
    governance_score: float
    methodology_version: str
    created_at: datetime
    model_config = {"from_attributes": True}


class ScoreCalcRequest(BaseModel):
    period: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/metrics", response_model=ESGMetricOut, status_code=status.HTTP_201_CREATED,
             summary="Record an ESG metric")
async def create_esg_metric(
    metric_in: ESGMetricCreate,
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    valid_categories = {"Environmental", "Social", "Governance"}
    if metric_in.category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Category must be one of: {valid_categories}")

    metric = ESGMetric(
        organization_id=uuid.UUID(org_id),
        category=metric_in.category,
        name=metric_in.name,
        value=metric_in.value,
        unit=metric_in.unit,
        period=metric_in.period,
    )
    db.add(metric)
    await db.commit()
    await db.refresh(metric)
    return metric


@router.get("/metrics", response_model=List[ESGMetricOut],
            summary="List ESG metrics for the current organization")
async def list_esg_metrics(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
    period: Optional[str] = None,
    category: Optional[str] = None,
) -> Any:
    stmt = select(ESGMetric).where(ESGMetric.organization_id == uuid.UUID(org_id))
    if period:
        stmt = stmt.where(ESGMetric.period == period)
    if category:
        stmt = stmt.where(ESGMetric.category == category)
    stmt = stmt.order_by(ESGMetric.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/scores/calculate", response_model=ESGScoreOut,
             summary="Calculate and store ESG score for a period")
async def calculate_and_store_score(
    request: ScoreCalcRequest,
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    org_uuid = uuid.UUID(org_id)

    scoring_result = await calculate_esg_score(db, org_uuid, request.period)
    score = await save_esg_score(db, org_uuid, scoring_result)
    return score


@router.get("/scores", response_model=List[ESGScoreOut],
            summary="List ESG scores for the current organization")
async def list_esg_scores(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    stmt = (
        select(ESGScore)
        .where(ESGScore.organization_id == uuid.UUID(org_id))
        .order_by(ESGScore.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/scores/latest", response_model=Optional[ESGScoreOut],
            summary="Get the latest ESG score")
async def get_latest_score(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    stmt = (
        select(ESGScore)
        .where(ESGScore.organization_id == uuid.UUID(org_id))
        .order_by(ESGScore.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalars().first()
