"""
Organization Pydantic schemas.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    """Payload for creating or onboarding a new organization."""
    name: str
    industry: Optional[str] = None
    country: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    financial_year_end: Optional[str] = None  # e.g. "March"
    reporting_year: Optional[int] = None
    # Reporting frameworks selected during onboarding
    frameworks: Optional[List[str]] = None  # ["GHG_PROTOCOL", "GRI", "BRSR", "ESRS"]


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    financial_year_end: Optional[str] = None
    reporting_year: Optional[int] = None


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    domain: Optional[str] = None
    subscription_tier: str
    is_active: bool
    industry: Optional[str] = None
    country: Optional[str] = None
    employee_count: Optional[int] = None
    reporting_year: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
