import uuid
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.db.session import get_db
from app.models.user import UserProfile

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",  # Even though we don't have this, it's required for OpenAPI docs
    auto_error=False,
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    """
    Validate the Supabase JWT and return the corresponding UserProfile.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    try:
        # Supabase uses HS256 and the project JWT secret
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},  # Audience verification might be tricky with Supabase depending on config
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise credentials_exception

    stmt = select(UserProfile).where(UserProfile.id == user_uuid)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


async def get_current_active_superuser(
    current_user: UserProfile = Depends(get_current_user),
) -> UserProfile:
    """
    Check if the current user has the SUPER_ADMIN role.
    """
    if current_user.role != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user


def require_role(allowed_roles: list[str]):
    """
    Dependency generator to check if the current user has one of the allowed roles.
    """
    async def role_checker(current_user: UserProfile = Depends(get_current_user)) -> UserProfile:
        if current_user.role not in allowed_roles and current_user.role != "SUPER_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the required role to perform this action.",
            )
        return current_user
    return role_checker


async def get_current_organization(current_user: UserProfile = Depends(get_current_user)) -> str:
    """
    Returns the organization ID for the current user. Raises 403 if they don't belong to one.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to any organization."
        )
    return str(current_user.organization_id)
