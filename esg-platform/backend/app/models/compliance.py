import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String, Boolean
from app.db.types import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin

class Framework(Base, TimestampMixin):
    __tablename__ = "frameworks"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

class FrameworkRequirement(Base, TimestampMixin):
    __tablename__ = "framework_requirements"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    framework_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("frameworks.id", ondelete="CASCADE"), index=True, nullable=False)
    requirement_code: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    required_data: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    required_evidence: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    applicability: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

class ComplianceRecord(Base, TimestampMixin):
    __tablename__ = "compliance_records"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    requirement_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("framework_requirements.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="MISSING", nullable=False) # COMPLETE, PARTIAL, MISSING, NEEDS_REVIEW, NOT_APPLICABLE
    evidence_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

