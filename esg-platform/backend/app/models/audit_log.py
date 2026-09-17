import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String
from app.db.types import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.base import TimestampMixin

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), index=True, nullable=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="SET NULL"), index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # LOGIN, UPLOAD, CREATE, UPDATE, DELETE...
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    old_value: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

