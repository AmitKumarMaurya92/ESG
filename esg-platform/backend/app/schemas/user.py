"""
User Pydantic schemas for request/response validation.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserProfileBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "EMPLOYEE"
    is_active: bool = True


class UserProfileResponse(UserProfileBase):
    """Returned to the frontend after authentication."""
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    """Fields a user can update about themselves."""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
