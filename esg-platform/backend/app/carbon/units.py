"""
Unit conversion utilities for the carbon calculation engine.

All conversion factors are based on standard references (IEA, IPCC, DEFRA).
Factors are stored here as constants — they are NOT sourced from an LLM.
"""

from typing import Optional


# ── Volume ────────────────────────────────────────────────────────────────────
# All to litres
VOLUME_TO_LITRES: dict[str, float] = {
    "litre": 1.0,
    "liter": 1.0,
    "l": 1.0,
    "gallon": 3.78541,
    "us_gallon": 3.78541,
    "uk_gallon": 4.54609,
    "m3": 1000.0,
    "cubic_metre": 1000.0,
    "cubic_meter": 1000.0,
    "ft3": 28.3168,
    "cubic_foot": 28.3168,
}

# ── Mass ──────────────────────────────────────────────────────────────────────
# All to kg
MASS_TO_KG: dict[str, float] = {
    "kg": 1.0,
    "kilogram": 1.0,
    "tonne": 1000.0,
    "metric_ton": 1000.0,
    "t": 1000.0,
    "lb": 0.453592,
    "pound": 0.453592,
    "short_ton": 907.185,
    "long_ton": 1016.05,
    "g": 0.001,
    "gram": 0.001,
}

# ── Energy ────────────────────────────────────────────────────────────────────
# All to kWh
ENERGY_TO_KWH: dict[str, float] = {
    "kwh": 1.0,
    "kilowatt_hour": 1.0,
    "mwh": 1000.0,
    "megawatt_hour": 1000.0,
    "gwh": 1_000_000.0,
    "gj": 277.778,
    "gigajoule": 277.778,
    "mj": 0.277778,
    "megajoule": 0.277778,
    "giga_joule": 277.778,
    "therm": 29.3071,
    "mmbtu": 293.071,
    "btu": 0.000293071,
}

# ── Distance ─────────────────────────────────────────────────────────────────
# All to km
DISTANCE_TO_KM: dict[str, float] = {
    "km": 1.0,
    "kilometre": 1.0,
    "kilometer": 1.0,
    "mile": 1.60934,
    "mi": 1.60934,
    "nautical_mile": 1.85200,
    "nm": 1.85200,
}

# ── Passenger-distance ────────────────────────────────────────────────────────
# All to passenger-km
PASSENGER_DIST_TO_PKM: dict[str, float] = {
    "pkm": 1.0,
    "passenger_km": 1.0,
    "passenger_mile": 1.60934,
}


def normalise_unit(value: float, unit: str) -> tuple[float, str, str]:
    """
    Normalise a value and unit to a canonical SI-like unit.

    Returns (normalised_value, canonical_unit, unit_type).
    unit_type is one of: 'volume', 'mass', 'energy', 'distance', 'passenger_distance', 'unknown'.
    """
    unit_lower = unit.lower().strip().replace("-", "_").replace(" ", "_")

    if unit_lower in VOLUME_TO_LITRES:
        return value * VOLUME_TO_LITRES[unit_lower], "litre", "volume"

    if unit_lower in MASS_TO_KG:
        return value * MASS_TO_KG[unit_lower], "kg", "mass"

    if unit_lower in ENERGY_TO_KWH:
        return value * ENERGY_TO_KWH[unit_lower], "kwh", "energy"

    if unit_lower in DISTANCE_TO_KM:
        return value * DISTANCE_TO_KM[unit_lower], "km", "distance"

    if unit_lower in PASSENGER_DIST_TO_PKM:
        return value * PASSENGER_DIST_TO_PKM[unit_lower], "pkm", "passenger_distance"

    # Unknown unit — return unchanged
    return value, unit, "unknown"


def is_compatible_unit(emission_factor_unit: str, activity_unit: str) -> bool:
    """
    Check if the emission factor unit type matches the activity unit type.
    """
    ef_unit_lower = emission_factor_unit.lower().strip().replace("-", "_").replace(" ", "_")
    act_unit_lower = activity_unit.lower().strip().replace("-", "_").replace(" ", "_")

    ef_type = _get_unit_type(ef_unit_lower)
    act_type = _get_unit_type(act_unit_lower)

    return ef_type == act_type or ef_type == "unknown" or act_type == "unknown"


def _get_unit_type(unit: str) -> str:
    if unit in VOLUME_TO_LITRES:
        return "volume"
    if unit in MASS_TO_KG:
        return "mass"
    if unit in ENERGY_TO_KWH:
        return "energy"
    if unit in DISTANCE_TO_KM:
        return "distance"
    if unit in PASSENGER_DIST_TO_PKM:
        return "passenger_distance"
    return "unknown"
