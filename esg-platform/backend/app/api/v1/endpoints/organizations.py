import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.db.session import get_db
from app.models.organization import Organization
from app.schemas.organization import OrganizationResponse, OrganizationUpdate

router = APIRouter()

@router.get("/me", response_model=OrganizationResponse)
async def read_organization_me(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get current user's organization.
    """
    stmt = select(Organization).where(Organization.id == uuid.UUID(org_id))
    result = await db.execute(stmt)
    org = result.scalars().first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@router.patch("/me", response_model=OrganizationResponse)
async def update_organization_me(
    org_in: OrganizationUpdate,
    org_id: str = Depends(deps.get_current_organization),
    current_user: Any = Depends(deps.require_role(["ORGANIZATION_ADMIN"])),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update current user's organization (requires ORGANIZATION_ADMIN).
    """
    stmt = select(Organization).where(Organization.id == uuid.UUID(org_id))
    result = await db.execute(stmt)
    org = result.scalars().first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    update_data = org_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)
        
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org
