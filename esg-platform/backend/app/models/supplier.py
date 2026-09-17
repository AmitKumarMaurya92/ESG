import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String, Float, Boolean, JSON
from app.db.types import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.base import TimestampMixin

class Supplier(Base, TimestampMixin):
    __tablename__ = "suppliers"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. IT, Manufacturing, Logistics
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False) # ACTIVE, INACTIVE, UNDER_REVIEW
    risk_level: Mapped[str] = mapped_column(String(50), default="UNKNOWN", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL, UNKNOWN
    spend_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    emissions_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

