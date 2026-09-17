import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String, Float, JSON
from app.db.types import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.base import TimestampMixin

class RiskEvent(Base, TimestampMixin):
    __tablename__ = "risk_events"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    metric: Mapped[str] = mapped_column(String(100), nullable=False)
    expected_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="open", nullable=False) # open, investigating, resolved
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

