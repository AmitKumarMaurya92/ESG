import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import exc

from app.api import deps
from app.db.session import get_db
from app.models.facility import Facility
from app.schemas.facility import FacilityCreate, FacilityResponse, FacilityUpdate

router = APIRouter()

@router.get("/", response_model=List[FacilityResponse])
async def list_facilities(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List all facilities for the current organization."""
    stmt = select(Facility).where(Facility.organization_id == uuid.UUID(org_id))
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=FacilityResponse, status_code=status.HTTP_201_CREATED)
async def create_facility(
    facility_in: FacilityCreate,
    org_id: str = Depends(deps.get_current_organization),
    current_user: Any = Depends(deps.require_role(["ORGANIZATION_ADMIN", "SUSTAINABILITY_MANAGER"])),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create new facility."""
    new_facility = Facility(
        **facility_in.model_dump(),
        organization_id=uuid.UUID(org_id)
    )
    db.add(new_facility)
    await db.commit()
    await db.refresh(new_facility)
    return new_facility

@router.get("/{facility_id}", response_model=FacilityResponse)
async def get_facility(
    facility_id: uuid.UUID,
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get a specific facility."""
    stmt = select(Facility).where(
        Facility.id == facility_id,
        Facility.organization_id == uuid.UUID(org_id)
    )
    result = await db.execute(stmt)
    facility = result.scalars().first()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility

@router.patch("/{facility_id}", response_model=FacilityResponse)
async def update_facility(
    facility_id: uuid.UUID,
    facility_in: FacilityUpdate,
    org_id: str = Depends(deps.get_current_organization),
    current_user: Any = Depends(deps.require_role(["ORGANIZATION_ADMIN", "SUSTAINABILITY_MANAGER"])),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update a specific facility."""
    stmt = select(Facility).where(
        Facility.id == facility_id,
        Facility.organization_id == uuid.UUID(org_id)
    )
    result = await db.execute(stmt)
    facility = result.scalars().first()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")

    update_data = facility_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(facility, field, value)

    db.add(facility)
    await db.commit()
    await db.refresh(facility)
    return facility

@router.delete("/{facility_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_facility(
    facility_id: uuid.UUID,
    org_id: str = Depends(deps.get_current_organization),
    current_user: Any = Depends(deps.require_role(["ORGANIZATION_ADMIN"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a facility."""
    stmt = select(Facility).where(
        Facility.id == facility_id,
        Facility.organization_id == uuid.UUID(org_id)
    )
    result = await db.execute(stmt)
    facility = result.scalars().first()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")

    await db.delete(facility)
    await db.commit()
