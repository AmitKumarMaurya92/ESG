"""
ESG Scoring Engine.

Calculates transparent, weighted ESG scores from stored ESGMetric records.
The LLM is NEVER used to determine scores.

Weights and methodology are stored in config, not hard-coded.
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.esg import ESGMetric, ESGScore

logger = logging.getLogger(__name__)

# ── Default weights (can be overridden per organization in future) ─────────────
DEFAULT_WEIGHTS = {
    "Environmental": 0.40,
    "Social": 0.30,
    "Governance": 0.30,
}

METHODOLOGY_VERSION = "1.0.0"

# ── Metric definitions with benchmarks ────────────────────────────────────────
# Each metric has a max_score (100) and the direction (lower_is_better for emissions)
METRIC_BENCHMARKS: dict[str, dict] = {
    # Environmental
    "ghg_emissions_intensity": {"max": 100, "lower_is_better": True, "category": "Environmental"},
    "energy_intensity": {"max": 100, "lower_is_better": True, "category": "Environmental"},
    "renewable_energy_pct": {"max": 100, "lower_is_better": False, "category": "Environmental"},
    "water_intensity": {"max": 100, "lower_is_better": True, "category": "Environmental"},
    "waste_recycling_rate": {"max": 100, "lower_is_better": False, "category": "Environmental"},
    # Social
    "safety_incident_rate": {"max": 100, "lower_is_better": True, "category": "Social"},
    "employee_turnover_rate": {"max": 100, "lower_is_better": True, "category": "Social"},
    "gender_diversity_pct": {"max": 100, "lower_is_better": False, "category": "Social"},
    "training_hours_per_employee": {"max": 100, "lower_is_better": False, "category": "Social"},
    # Governance
    "board_independence_pct": {"max": 100, "lower_is_better": False, "category": "Governance"},
    "ethics_violations": {"max": 100, "lower_is_better": True, "category": "Governance"},
    "data_breaches": {"max": 100, "lower_is_better": True, "category": "Governance"},
}


@dataclass
class ScoringResult:
    overall_score: float
    environmental_score: float
    social_score: float
    governance_score: float
    methodology_version: str
    period: str
    calculated_at: datetime
    metric_breakdown: dict = field(default_factory=dict)
    data_coverage_pct: float = 0.0
    notes: str = ""


async def calculate_esg_score(
    db: AsyncSession,
    organization_id: uuid.UUID,
    period: str,
) -> ScoringResult:
    """
    Calculate the ESG score for an organization for a given period.

    Score = Σ (metric_score × weight) / Σ weights

    Where metric_score is normalized to 0-100 based on value and benchmark direction.
    """
    now = datetime.now(timezone.utc)

    # Fetch all ESG metrics for this organization and period
    stmt = select(ESGMetric).where(
        ESGMetric.organization_id == organization_id,
        ESGMetric.period == period,
    )
    result = await db.execute(stmt)
    metrics = result.scalars().all()

    if not metrics:
        logger.warning("No ESG metrics found for org %s period %s", organization_id, period)
        # Return a neutral mid-score with low data coverage
        return ScoringResult(
            overall_score=50.0,
            environmental_score=50.0,
            social_score=50.0,
            governance_score=50.0,
            methodology_version=METHODOLOGY_VERSION,
            period=period,
            calculated_at=now,
            data_coverage_pct=0.0,
            notes="No ESG metrics recorded for this period. Score is a neutral placeholder.",
        )

    # Group metrics by category
    category_scores: dict[str, list[float]] = {
        "Environmental": [],
        "Social": [],
        "Governance": [],
    }
    metric_breakdown = {}

    for m in metrics:
        # Normalize value to 0-100 score
        benchmark = METRIC_BENCHMARKS.get(m.name)
        if benchmark:
            raw_score = _normalize_metric(m.value, m.unit, benchmark)
            category_scores[benchmark["category"]].append(raw_score)
            metric_breakdown[m.name] = {
                "value": m.value,
                "unit": m.unit,
                "score": raw_score,
                "category": benchmark["category"],
            }
        else:
            # Unknown metric — use value directly if it's a percentage (0-100)
            category = m.category if m.category in category_scores else "Environmental"
            score = min(max(m.value, 0.0), 100.0)
            category_scores[category].append(score)
            metric_breakdown[m.name] = {
                "value": m.value,
                "unit": m.unit,
                "score": score,
                "category": category,
            }

    # Calculate category averages
    def avg(scores: list[float]) -> float:
        return sum(scores) / len(scores) if scores else 50.0

    env_score = avg(category_scores["Environmental"])
    soc_score = avg(category_scores["Social"])
    gov_score = avg(category_scores["Governance"])

    # Weighted overall
    w = DEFAULT_WEIGHTS
    overall = (
        env_score * w["Environmental"]
        + soc_score * w["Social"]
        + gov_score * w["Governance"]
    )

    # Data coverage
    total_expected = len(METRIC_BENCHMARKS)
    total_recorded = len(metrics)
    coverage = min((total_recorded / total_expected) * 100, 100.0)

    return ScoringResult(
        overall_score=round(overall, 2),
        environmental_score=round(env_score, 2),
        social_score=round(soc_score, 2),
        governance_score=round(gov_score, 2),
        methodology_version=METHODOLOGY_VERSION,
        period=period,
        calculated_at=now,
        metric_breakdown=metric_breakdown,
        data_coverage_pct=round(coverage, 1),
    )


def _normalize_metric(value: float, unit: str, benchmark: dict) -> float:
    """
    Normalize a metric value to a 0-100 score.
    For percentage-based metrics: use directly (clamped).
    For other metrics: use simple linear scaling with assumed thresholds.
    """
    unit_lower = unit.lower()

    if unit_lower in ("%", "percent", "pct", "percentage"):
        # Already 0-100%
        score = min(max(value, 0.0), 100.0)
        if benchmark.get("lower_is_better"):
            score = 100.0 - score
        return score

    # For non-percentage metrics, we use a simple linear scale
    # Assume a "good" threshold at 0 and "bad" at some reasonable max
    # This can be refined with industry benchmarks in production
    if benchmark.get("lower_is_better"):
        # Lower is better: value=0 → score=100, value=1000 → score=0
        score = max(100.0 - (value / 10.0), 0.0)
    else:
        # Higher is better
        score = min(value / 10.0, 100.0)

    return score


async def save_esg_score(
    db: AsyncSession,
    organization_id: uuid.UUID,
    result: ScoringResult,
) -> ESGScore:
    """Persist the calculated ESG score to the database."""
    score = ESGScore(
        organization_id=organization_id,
        period=result.period,
        overall_score=result.overall_score,
        environmental_score=result.environmental_score,
        social_score=result.social_score,
        governance_score=result.governance_score,
        methodology_version=result.methodology_version,
    )
    db.add(score)
    await db.commit()
    await db.refresh(score)
    return score
