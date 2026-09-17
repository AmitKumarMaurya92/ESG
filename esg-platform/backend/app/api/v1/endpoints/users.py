import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.db.session import get_db
from app.models.user import UserProfile
from app.schemas.user import UserProfileResponse, UserProfileUpdate

router = APIRouter()

@router.get("/me", response_model=UserProfileResponse)
async def read_user_me(
    current_user: UserProfile = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user profile.
    """
    return current_user

@router.patch("/me", response_model=UserProfileResponse)
async def update_user_me(
    user_in: UserProfileUpdate,
    current_user: UserProfile = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update current user profile.
    """
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    if user_in.avatar_url is not None:
        current_user.avatar_url = user_in.avatar_url
        
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user
