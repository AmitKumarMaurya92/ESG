"""
Core carbon calculation engine.

CO2e = Activity Data × Emission Factor (kg CO2e per unit)

This module is DETERMINISTIC. LLMs are never used to compute final emission values.
Every calculation stores:
  - emission_factor_id
  - emission_factor_version
  - source
  - calculation_method
  - calculation_timestamp
  - resulting CO2e
"""

import uuid
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.emission_factor import EmissionFactor
from app.carbon.units import normalise_unit

logger = logging.getLogger(__name__)


@dataclass
class CalculationResult:
    """Result of a CO2e calculation, fully traceable."""
    co2e_kg: float                          # kilograms of CO2e
    emission_factor_id: Optional[uuid.UUID]
    emission_factor_value: float            # factor used (kg CO2e per canonical unit)
    emission_factor_unit: str
    emission_factor_source: str
    emission_factor_version: str
    activity_value_raw: float               # original submitted value
    activity_unit_raw: str                  # original submitted unit
    activity_value_normalised: float        # after unit conversion
    activity_unit_normalised: str
    calculation_method: str
    calculated_at: datetime
    notes: str = ""


async def lookup_emission_factor(
    db: AsyncSession,
    scope: int,
    category: str,
    activity_unit: str,
    country: str = "global",
) -> Optional[EmissionFactor]:
    """
    Retrieve the most recent valid emission factor for a given scope, category, and unit type.
    Tries country-specific first, then falls back to 'global'.
    """
    canonical_value, canonical_unit, unit_type = normalise_unit(1.0, activity_unit)

    async def _query(country_filter: str) -> Optional[EmissionFactor]:
        stmt = (
            select(EmissionFactor)
            .where(
                EmissionFactor.scope == scope,
                EmissionFactor.category == category,
                EmissionFactor.country.in_([country_filter, "global"]),
            )
            .order_by(EmissionFactor.created_at.desc())
        )
        result = await db.execute(stmt)
        factors = result.scalars().all()

        # Prefer matching unit type (litre→volume, kwh→energy etc.)
        for ef in factors:
            ef_canonical_value, ef_canonical_unit, ef_unit_type = normalise_unit(1.0, ef.unit)
            if ef_unit_type == unit_type or unit_type == "unknown":
                return ef

        # If no unit-type match, return first available
        return factors[0] if factors else None

    # Try country-specific first
    if country and country.lower() != "global":
        ef = await _query(country)
        if ef:
            return ef

    return await _query("global")


async def calculate_co2e(
    db: AsyncSession,
    scope: int,
    category: str,
    activity_value: float,
    activity_unit: str,
    country: str = "global",
    calculation_method: str = "location-based",
) -> CalculationResult:
    """
    Deterministically calculate CO2e for an activity.

    Algorithm:
    1. Normalise activity value to canonical unit
    2. Lookup best matching emission factor
    3. Normalise emission factor unit to same canonical unit
    4. CO2e = normalised_activity × (factor / factor_unit_scale)

    Falls back to a default factor (2.5 kg CO2e per unit) if none found.
    """
    now = datetime.now(timezone.utc)

    # Step 1: normalise activity
    norm_activity, canonical_unit, unit_type = normalise_unit(activity_value, activity_unit)

    # Step 2: lookup emission factor
    ef = await lookup_emission_factor(db, scope, category, activity_unit, country)

    if ef is None:
        logger.warning(
            "No emission factor found for scope=%d category=%s unit=%s. Using fallback.",
            scope, category, activity_unit
        )
        co2e = norm_activity * 2.5
        return CalculationResult(
            co2e_kg=co2e,
            emission_factor_id=None,
            emission_factor_value=2.5,
            emission_factor_unit="per_unit",
            emission_factor_source="fallback_estimate",
            emission_factor_version="0.0",
            activity_value_raw=activity_value,
            activity_unit_raw=activity_unit,
            activity_value_normalised=norm_activity,
            activity_unit_normalised=canonical_unit,
            calculation_method=calculation_method,
            calculated_at=now,
            notes="FALLBACK: No emission factor found. Value is an estimate only.",
        )

    # Step 3: normalise the emission factor unit
    ef_norm_scale, ef_canonical_unit, ef_unit_type = normalise_unit(1.0, ef.unit)

    # CO2e = normalised_activity / ef_norm_scale * ef.factor
    # But ef_norm_scale converts 1 ef.unit → ef_canonical_unit
    # So we need activity in the same canonical unit
    if ef_unit_type != "unknown" and unit_type != "unknown" and ef_unit_type == unit_type:
        # Both in same unit type — convert activity canonical to ef canonical
        activity_in_ef_canonical_units = norm_activity
        co2e = activity_in_ef_canonical_units * ef.factor
    else:
        # Unit type mismatch or unknown — multiply directly
        co2e = activity_value * ef.factor
        norm_activity = activity_value
        canonical_unit = activity_unit

    logger.info(
        "Calculated CO2e: %.2f kgCO2e for %.2f %s [scope=%d category=%s factor=%s]",
        co2e, activity_value, activity_unit, scope, category, ef.factor
    )

    return CalculationResult(
        co2e_kg=co2e,
        emission_factor_id=ef.id,
        emission_factor_value=ef.factor,
        emission_factor_unit=ef.unit,
        emission_factor_source=ef.source,
        emission_factor_version=ef.version,
        activity_value_raw=activity_value,
        activity_unit_raw=activity_unit,
        activity_value_normalised=norm_activity,
        activity_unit_normalised=canonical_unit,
        calculation_method=calculation_method,
        calculated_at=now,
    )
