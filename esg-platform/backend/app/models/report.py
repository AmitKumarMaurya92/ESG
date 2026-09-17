import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.base import TimestampMixin

class Report(Base, TimestampMixin):
    __tablename__ = "reports"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    generated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(100), nullable=False) # Carbon, ESG, Compliance, Executive, Supplier
    period: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    format: Mapped[str] = mapped_column(String(50), nullable=False) # PDF, Excel, CSV
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="GENERATING", nullable=False) # GENERATING, COMPLETED, FAILED
    methodology_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    data_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
