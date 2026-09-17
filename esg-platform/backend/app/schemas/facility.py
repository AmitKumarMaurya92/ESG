"""
Facility Pydantic schemas.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FacilityCreate(BaseModel):
    name: str
    country: str
    state_province: Optional[str] = None
    code: Optional[str] = None
    facility_type: str = "office"  # office | manufacturing | warehouse | data_center | retail
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    is_active: bool = True


class FacilityUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    state_province: Optional[str] = None
    code: Optional[str] = None
    facility_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    is_active: Optional[bool] = None


class FacilityResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: Optional[str] = None
    country: str
    state_province: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    facility_type: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
