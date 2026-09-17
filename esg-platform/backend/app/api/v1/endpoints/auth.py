import uuid
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from app.api import deps
from app.core.config import settings
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import UserProfile

router = APIRouter()


class SyncUserRequest(BaseModel):
    organization_name: str
    full_name: str


@router.post("/sync", status_code=status.HTTP_201_CREATED)
async def sync_user(
    request: SyncUserRequest,
    token: str = Depends(deps.oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Synchronize a newly registered Supabase Auth user to the local database.
    This creates an Organization and UserProfile.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
        )

    try:
        # Decode the token directly to get the user id and email
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},
        )
        user_id_str: str = payload.get("sub")
        email: str = payload.get("email")
        if not user_id_str or not email:
            raise ValueError("Invalid payload")
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    # Check if user already exists
    stmt = select(UserProfile).where(UserProfile.id == user_uuid)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()

    if existing_user:
        return {"message": "User already synchronized", "user_id": str(existing_user.id)}

    # Create Organization
    # Create a slug from the name (simple lowercase and replace spaces)
    slug = request.organization_name.lower().replace(" ", "-")
    # Check if slug exists, if so append something random (or just fail for now)
    stmt_org = select(Organization).where(Organization.slug == slug)
    result_org = await db.execute(stmt_org)
    if result_org.scalars().first():
        slug = f"{slug}-{str(uuid.uuid4())[:8]}"

    new_org = Organization(
        name=request.organization_name,
        slug=slug,
    )
    db.add(new_org)
    await db.flush()  # To get new_org.id

    # Create UserProfile
    new_user = UserProfile(
        id=user_uuid,
        email=email,
        full_name=request.full_name,
        role="ORGANIZATION_ADMIN",  # The creator is the admin
        organization_id=new_org.id,
    )
    db.add(new_user)
    
    await db.commit()
    return {"message": "User and organization synchronized successfully"}
