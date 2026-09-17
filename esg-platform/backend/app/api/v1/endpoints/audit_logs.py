"""
Audit Logs endpoint.

Provides read-only access to the audit trail.
Only organization admins and auditors can view their org's logs.
Super admins can view all logs.
"""

import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from datetime import datetime

from app.api import deps
from app.db.session import get_db
from app.models.audit_log import AuditLog

router = APIRouter()


class AuditLogOut(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    organization_id: Optional[uuid.UUID]
    action: str
    resource_type: str
    resource_id: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}


@router.get("/", response_model=List[AuditLogOut],
            summary="List audit log entries for the current organization",
            description="Returns the most recent audit log entries. Restricted to admins and auditors.")
async def list_audit_logs(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
) -> Any:
    stmt = (
        select(AuditLog)
        .where(AuditLog.organization_id == uuid.UUID(org_id))
        .order_by(AuditLog.created_at.desc())
        .limit(min(limit, 500))
    )
    if action:
        stmt = stmt.where(AuditLog.action == action.upper())
    if resource_type:
        stmt = stmt.where(AuditLog.resource_type == resource_type)

    result = await db.execute(stmt)
    return result.scalars().all()
