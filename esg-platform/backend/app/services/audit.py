"""
Audit logging service.

Every significant action is recorded for compliance and security audit trails.
"""

import logging
import uuid
from typing import Optional, Any
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


async def log_action(
    db: AsyncSession,
    user_id: Optional[uuid.UUID],
    organization_id: Optional[uuid.UUID],
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    old_value: Optional[Any] = None,
    new_value: Optional[Any] = None,
    ip_address: Optional[str] = None,
) -> None:
    """
    Create an audit log entry.

    Actions include:
    LOGIN, LOGOUT, UPLOAD, CREATE, UPDATE, DELETE, CALCULATION,
    REPORT_GENERATED, COMPLIANCE_UPDATE, API_ACCESS, SUPPLIER_SUBMISSION, etc.
    """
    try:
        entry = AuditLog(
            user_id=user_id,
            organization_id=organization_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            old_value=str(old_value)[:2048] if old_value is not None else None,
            new_value=str(new_value)[:2048] if new_value is not None else None,
            ip_address=ip_address,
        )
        db.add(entry)
        await db.commit()
    except Exception as e:
        # Audit logging must never break the main application flow
        logger.error("Failed to write audit log: %s", e)
