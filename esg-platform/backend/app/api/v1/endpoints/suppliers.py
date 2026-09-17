import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.db.session import get_db
from app.models.supplier import Supplier
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class SupplierCreate(BaseModel):
    name: str
    contact_email: Optional[str] = None
    category: str
    status: str = "ACTIVE"
    risk_level: str = "UNKNOWN"

class SupplierResponse(SupplierCreate):
    id: uuid.UUID
    created_at: datetime
    model_config = {"from_attributes": True}

@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier_in: SupplierCreate,
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    new_supplier = Supplier(
        **supplier_in.model_dump(),
        organization_id=uuid.UUID(org_id)
    )
    db.add(new_supplier)
    await db.commit()
    await db.refresh(new_supplier)
    return new_supplier

@router.get("/", response_model=List[SupplierResponse])
async def list_suppliers(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    stmt = select(Supplier).where(Supplier.organization_id == uuid.UUID(org_id)).order_by(Supplier.name)
    result = await db.execute(stmt)
    return result.scalars().all()
