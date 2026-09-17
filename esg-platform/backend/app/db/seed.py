"""
Database seed script.

Creates realistic sample data for development and demo purposes:
- Emission factors (GHG Protocol / DEFRA based)
- Compliance frameworks (GHG Protocol, GRI, BRSR)
- Framework requirements

Run with:
    cd backend
    python -m app.db.seed
"""

import asyncio
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import AsyncSessionLocal as async_session_factory
from app.models.emission_factor import EmissionFactor
from app.models.compliance import Framework, FrameworkRequirement

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Emission Factors ──────────────────────────────────────────────────────────
# Source: DEFRA 2024 / IPCC AR6 / GHG Protocol
# All factors are in kg CO2e per unit

EMISSION_FACTORS = [
    # ── Scope 1 — Stationary Combustion ──────────────────────────────────────
    {
        "name": "Natural Gas - Stationary Combustion",
        "category": "natural_gas",
        "scope": 1,
        "country": "global",
        "unit": "kwh",
        "factor": 0.18316,  # kg CO2e per kWh (gross calorific value)
        "co2_factor": 0.18251,
        "ch4_factor": 0.000036,
        "n2o_factor": 0.000034,
        "source": "DEFRA 2024",
        "source_url": "https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024",
        "version": "DEFRA-2024",
        "methodology": "GHG Protocol - Stationary Combustion",
    },
    {
        "name": "Diesel - Stationary Combustion",
        "category": "diesel",
        "scope": 1,
        "country": "global",
        "unit": "litre",
        "factor": 2.68784,  # kg CO2e per litre
        "co2_factor": 2.64774,
        "ch4_factor": 0.00067,
        "n2o_factor": 0.03949,
        "source": "DEFRA 2024",
        "source_url": "https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024",
        "version": "DEFRA-2024",
        "methodology": "GHG Protocol - Stationary Combustion",
    },
    {
        "name": "Petrol (Gasoline) - Stationary Combustion",
        "category": "petrol",
        "scope": 1,
        "country": "global",
        "unit": "litre",
        "factor": 2.30825,  # kg CO2e per litre
        "co2_factor": 2.27218,
        "source": "DEFRA 2024",
        "version": "DEFRA-2024",
        "methodology": "GHG Protocol - Stationary Combustion",
    },
    {
        "name": "LPG (Liquefied Petroleum Gas)",
        "category": "lpg",
        "scope": 1,
        "country": "global",
        "unit": "litre",
        "factor": 1.55536,  # kg CO2e per litre
        "source": "DEFRA 2024",
        "version": "DEFRA-2024",
        "methodology": "GHG Protocol - Stationary Combustion",
    },
    {
        "name": "Diesel - Mobile Combustion",
        "category": "mobile_combustion_diesel",
        "scope": 1,
        "country": "global",
        "unit": "litre",
        "factor": 2.68784,
        "source": "DEFRA 2024",
        "version": "DEFRA-2024",
        "methodology": "GHG Protocol - Mobile Combustion",
    },
    {
        "name": "Petrol - Mobile Combustion",
        "category": "mobile_combustion_petrol",
        "scope": 1,
        "country": "global",
        "unit": "litre",
        "factor": 2.30825,
        "source": "DEFRA 2024",
        "version": "DEFRA-2024",
        "methodology": "GHG Protocol - Mobile Combustion",
    },
    {
        "name": "Refrigerant R410A",
        "category": "refrigerants",
        "scope": 1,
        "country": "global",
        "unit": "kg",
        "factor": 2088.0,  # GWP of R410A
        "source": "IPCC AR6",
        "version": "IPCC-AR6",
        "methodology": "GHG Protocol - Fugitive Emissions",
    },
    # ── Scope 2 — Purchased Electricity ──────────────────────────────────────
    {
        "name": "Electricity - UK Grid (Location-Based)",
        "category": "purchased_electricity",
        "scope": 2,
        "country": "GB",
        "unit": "kwh",
        "factor": 0.20713,  # kg CO2e per kWh
        "source": "DEFRA 2024 / National Grid",
        "version": "DEFRA-2024",
        "methodology": "GHG Protocol Scope 2 - Location-Based",
    },
    {
        "name": "Electricity - India Grid (Location-Based)",
        "category": "purchased_electricity",
        "scope": 2,
        "country": "IN",
        "unit": "kwh",
        "factor": 0.7082,  # kg CO2e per kWh (CEA 2024)
        "source": "CEA 2024 - CO2 Baseline Database for Indian Power Sector",
        "source_url": "https://cea.nic.in/",
        "version": "CEA-2024",
        "methodology": "GHG Protocol Scope 2 - Location-Based",
    },
    {
        "name": "Electricity - US Average Grid (Location-Based)",
        "category": "purchased_electricity",
        "scope": 2,
        "country": "US",
        "unit": "kwh",
        "factor": 0.3866,  # kg CO2e per kWh (EPA eGRID 2023)
        "source": "EPA eGRID 2023",
        "source_url": "https://www.epa.gov/egrid",
        "version": "eGRID-2023",
        "methodology": "GHG Protocol Scope 2 - Location-Based",
    },
    {
        "name": "Electricity - Global Average (Location-Based)",
        "category": "purchased_electricity",
        "scope": 2,
        "country": "global",
        "unit": "kwh",
        "factor": 0.4930,  # kg CO2e per kWh (IEA World 2022)
        "source": "IEA 2022 - Emission Factors",
        "source_url": "https://www.iea.org/data-and-statistics/data-product/co2-emissions-from-fuel-combustion",
        "version": "IEA-2022",
        "methodology": "GHG Protocol Scope 2 - Location-Based",
    },
    {
        "name": "Purchased Steam",
        "category": "purchased_steam",
        "scope": 2,
        "country": "global",
        "unit": "kwh",
        "factor": 0.14,
        "source": "DEFRA 2024",
        "version": "DEFRA-2024",
        "methodology": "GHG Protocol Scope 2",
    },
    # ── Scope 3 ───────────────────────────────────────────────────────────────
    {
        "name": "Business Travel - Short-Haul Flight (Economy)",
        "category": "business_travel",
        "scope": 3,
        "country": "global",
        "unit": "pkm",
        "factor": 0.15553,  # kg CO2e per passenger-km
        "source": "DEFRA 2024",
        "version": "DEFRA-2024",
        "methodology": "GHG Protocol Scope 3 - Category 6",
    },
    {
        "name": "Business Travel - Long-Haul Flight (Economy)",
        "category": "business_travel_longhaul",
        "scope": 3,
        "country": "global",
        "unit": "pkm",
        "factor": 0.14787,
        "source": "DEFRA 2024",
        "version": "DEFRA-2024",
        "methodology": "GHG Protocol Scope 3 - Category 6",
    },
    {
        "name": "Employee Commuting - Average Car",
        "category": "employee_commuting",
        "scope": 3,
        "country": "global",
        "unit": "km",
        "factor": 0.16844,  # kg CO2e per km
        "source": "DEFRA 2024",
        "version": "DEFRA-2024",
        "methodology": "GHG Protocol Scope 3 - Category 7",
    },
    {
        "name": "Upstream Transportation - Heavy Goods Vehicle (Road)",
        "category": "upstream_transportation",
        "scope": 3,
        "country": "global",
        "unit": "tkm",  # tonne-km
        "factor": 0.10250,  # kg CO2e per tonne-km
        "source": "DEFRA 2024",
        "version": "DEFRA-2024",
        "methodology": "GHG Protocol Scope 3 - Category 4",
    },
    {
        "name": "Waste - Landfill (Mixed Municipal)",
        "category": "waste_generated",
        "scope": 3,
        "country": "global",
        "unit": "kg",
        "factor": 0.58600,  # kg CO2e per kg waste
        "source": "DEFRA 2024",
        "version": "DEFRA-2024",
        "methodology": "GHG Protocol Scope 3 - Category 5",
    },
    {
        "name": "Waste - Recycling (Mixed)",
        "category": "waste_recycling",
        "scope": 3,
        "country": "global",
        "unit": "kg",
        "factor": 0.02100,
        "source": "DEFRA 2024",
        "version": "DEFRA-2024",
        "methodology": "GHG Protocol Scope 3 - Category 5",
    },
]


# ── Compliance Frameworks ─────────────────────────────────────────────────────

FRAMEWORKS = [
    {
        "name": "GHG Protocol",
        "version": "2015",
        "description": "The GHG Protocol Corporate Accounting and Reporting Standard provides requirements and guidance for companies and other organizations preparing a corporate-level GHG emissions inventory.",
        "requirements": [
            {"code": "GHG-1.1", "title": "Scope 1 Emissions Reporting", "desc": "Report all direct GHG emissions from owned or controlled sources.", "data": "Scope 1 activity data by source category", "evidence": "Meter readings, fuel purchase records, MSDS sheets"},
            {"code": "GHG-1.2", "title": "Scope 2 Emissions Reporting", "desc": "Report indirect GHG emissions from purchased or acquired electricity, steam, heat, or cooling.", "data": "Energy purchase records, supplier emission factors", "evidence": "Utility bills, energy purchase invoices"},
            {"code": "GHG-1.3", "title": "Scope 3 Emissions Assessment", "desc": "Assess and report material Scope 3 emission categories.", "data": "Relevant Scope 3 category data", "evidence": "Supplier data, spend data, travel records"},
            {"code": "GHG-2.1", "title": "Emission Factor Documentation", "desc": "Document all emission factors used with source, version, and date.", "data": "Emission factor registry", "evidence": "Emission factor references"},
            {"code": "GHG-2.2", "title": "Organizational Boundary Setting", "desc": "Define organizational boundaries using equity share or control approach.", "data": "Organizational structure", "evidence": "Corporate structure documentation"},
            {"code": "GHG-3.1", "title": "Base Year Definition", "desc": "Define a base year for tracking emissions over time.", "data": "Base year emissions", "evidence": "Historical emissions inventory"},
            {"code": "GHG-3.2", "title": "Inventory Quality Assurance", "desc": "Implement QA/QC procedures for the emissions inventory.", "data": "QA/QC process documentation", "evidence": "Internal audit records"},
        ],
    },
    {
        "name": "GRI",
        "version": "2021",
        "description": "Global Reporting Initiative Universal Standards 2021. The world's most widely used sustainability reporting framework.",
        "requirements": [
            {"code": "GRI-302-1", "title": "Energy Consumption Within Organization", "desc": "Report energy consumed from non-renewable and renewable sources.", "data": "Energy consumption by source", "evidence": "Utility bills, fuel records"},
            {"code": "GRI-302-3", "title": "Energy Intensity", "desc": "Report energy intensity ratio with organization-specific metric.", "data": "Energy intensity formula", "evidence": "Financial/production records"},
            {"code": "GRI-305-1", "title": "Direct (Scope 1) GHG Emissions", "desc": "Report gross Scope 1 GHG emissions in metric tons CO2 equivalent.", "data": "Scope 1 data by source", "evidence": "Fuel consumption records"},
            {"code": "GRI-305-2", "title": "Energy Indirect (Scope 2) GHG Emissions", "desc": "Report gross location-based and market-based Scope 2 GHG emissions.", "data": "Electricity and energy purchase data", "evidence": "Utility bills"},
            {"code": "GRI-305-3", "title": "Other Indirect (Scope 3) GHG Emissions", "desc": "Report gross Scope 3 GHG emissions by category.", "data": "Scope 3 activity data by category", "evidence": "Supplier surveys, travel records"},
            {"code": "GRI-305-4", "title": "GHG Emissions Intensity", "desc": "Report GHG emissions intensity ratio.", "data": "GHG intensity calculation", "evidence": "Emissions and activity data"},
            {"code": "GRI-306-1", "title": "Waste Generation", "desc": "Report waste generated in metric tons by composition and disposal route.", "data": "Waste records by type and route", "evidence": "Waste manifests, contractor receipts"},
            {"code": "GRI-303-3", "title": "Water Withdrawal", "desc": "Report total water withdrawal by source.", "data": "Water consumption data", "evidence": "Meter readings, utility bills"},
            {"code": "GRI-401-1", "title": "New Employee Hires and Employee Turnover", "desc": "Report total number and rate of new hires and turnover.", "data": "HR data", "evidence": "HR system records"},
            {"code": "GRI-403-9", "title": "Work-Related Injuries", "desc": "Report work-related injuries including fatalities.", "data": "Safety incident records", "evidence": "Incident reports, regulatory filings"},
        ],
    },
    {
        "name": "BRSR",
        "version": "2023",
        "description": "Business Responsibility and Sustainability Report - mandatory for top 1000 listed companies in India (SEBI).",
        "requirements": [
            {"code": "BRSR-P1-E1", "title": "GHG Emissions - Scope 1", "desc": "Disclose Scope 1 GHG emissions in metric tons CO2 equivalent.", "data": "Scope 1 emissions data", "evidence": "Source activity data, emission factor references"},
            {"code": "BRSR-P1-E2", "title": "GHG Emissions - Scope 2", "desc": "Disclose Scope 2 GHG emissions in metric tons CO2 equivalent.", "data": "Scope 2 emissions data", "evidence": "Electricity bills, grid emission factors"},
            {"code": "BRSR-P1-E3", "title": "GHG Emissions Intensity", "desc": "Disclose GHG emissions intensity per rupee of turnover.", "data": "GHG intensity per turnover", "evidence": "Financial and emissions data"},
            {"code": "BRSR-P1-E4", "title": "Energy Consumption", "desc": "Total energy consumption from renewable and non-renewable sources.", "data": "Energy consumption breakdown", "evidence": "Utility bills, meter readings"},
            {"code": "BRSR-P1-E5", "title": "Water Withdrawal", "desc": "Water withdrawal by source.", "data": "Water meter data", "evidence": "Utility bills"},
            {"code": "BRSR-P1-E6", "title": "Waste Management", "desc": "Hazardous and non-hazardous waste generated and disposed.", "data": "Waste records", "evidence": "Waste manifests"},
            {"code": "BRSR-P3-S1", "title": "Employee Well-Being", "desc": "Percentage of employees covered by health insurance, accident cover, etc.", "data": "HR benefits data", "evidence": "Insurance policy records"},
            {"code": "BRSR-P4-G1", "title": "Anti-Corruption Policy", "desc": "Disclose anti-corruption policies and training.", "data": "Policy documentation, training records", "evidence": "Policy documents"},
        ],
    },
    {
        "name": "ESRS",
        "version": "2023",
        "description": "European Sustainability Reporting Standards - mandatory for large EU companies under CSRD.",
        "requirements": [
            {"code": "ESRS-E1-6", "title": "Gross Scopes 1, 2, 3 GHG Emissions", "desc": "Disclose gross Scope 1, 2 and 3 GHG emissions.", "data": "Scope 1, 2, 3 emissions data", "evidence": "Activity data and emission factors"},
            {"code": "ESRS-E1-7", "title": "GHG Removals and GHG Mitigation", "desc": "Disclose carbon removals and credits used.", "data": "Carbon credit records", "evidence": "Verified offset certificates"},
            {"code": "ESRS-E1-9", "title": "Anticipated Financial Effects from Climate Change", "desc": "Quantify financial exposure to climate-related transition and physical risks.", "data": "Financial risk assessments", "evidence": "Climate scenario analysis"},
            {"code": "ESRS-E2-1", "title": "Pollution of Air, Water, Soil", "desc": "Disclose pollutant emissions to air, water and soil.", "data": "Environmental monitoring data", "evidence": "Regulatory reports"},
            {"code": "ESRS-E3-1", "title": "Water and Marine Resources", "desc": "Disclose water consumption, withdrawal and discharge.", "data": "Water consumption data", "evidence": "Meter readings"},
            {"code": "ESRS-S1-1", "title": "Own Workforce Policies", "desc": "Disclose policies related to own workforce.", "data": "HR policies", "evidence": "Policy documents"},
            {"code": "ESRS-G1-1", "title": "Business Conduct Policies", "desc": "Disclose policies on anti-bribery and corruption.", "data": "Governance policies", "evidence": "Policy documentation"},
        ],
    },
]


async def seed_emission_factors(db: AsyncSession) -> None:
    """Seed emission factors if they don't already exist."""
    # Check if already seeded
    existing = await db.execute(select(EmissionFactor).limit(1))
    if existing.scalars().first():
        logger.info("Emission factors already seeded, skipping.")
        return

    logger.info("Seeding %d emission factors...", len(EMISSION_FACTORS))
    for ef_data in EMISSION_FACTORS:
        ef = EmissionFactor(
            name=ef_data["name"],
            category=ef_data["category"],
            scope=ef_data["scope"],
            country=ef_data["country"],
            unit=ef_data["unit"],
            factor=ef_data["factor"],
            co2_factor=ef_data.get("co2_factor"),
            ch4_factor=ef_data.get("ch4_factor"),
            n2o_factor=ef_data.get("n2o_factor"),
            source=ef_data["source"],
            source_url=ef_data.get("source_url"),
            version=ef_data["version"],
            valid_from="2024-01-01",
            methodology=ef_data.get("methodology"),
        )
        db.add(ef)

    await db.commit()
    logger.info("✓ Emission factors seeded.")


async def seed_frameworks(db: AsyncSession) -> None:
    """Seed compliance frameworks and requirements if they don't already exist."""
    existing = await db.execute(select(Framework).limit(1))
    if existing.scalars().first():
        logger.info("Frameworks already seeded, skipping.")
        return

    logger.info("Seeding %d compliance frameworks...", len(FRAMEWORKS))

    for fw_data in FRAMEWORKS:
        fw = Framework(
            name=fw_data["name"],
            version=fw_data["version"],
            description=fw_data["description"],
        )
        db.add(fw)
        await db.flush()  # Get the generated ID

        for req_data in fw_data["requirements"]:
            req = FrameworkRequirement(
                framework_id=fw.id,
                requirement_code=req_data["code"],
                title=req_data["title"],
                description=req_data.get("desc"),
                required_data=req_data.get("data"),
                required_evidence=req_data.get("evidence"),
                source=fw_data["name"],
            )
            db.add(req)

    await db.commit()
    logger.info("✓ Compliance frameworks seeded.")


async def main() -> None:
    """Run all seed operations."""
    logger.info("Starting database seed...")

    async with async_session_factory() as db:
        await seed_emission_factors(db)
        await seed_frameworks(db)

    logger.info("Database seed complete!")


if __name__ == "__main__":
    asyncio.run(main())
