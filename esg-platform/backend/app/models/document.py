import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin

class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    uploader_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="SET NULL"), nullable=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    document_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    processing_status: Mapped[str] = mapped_column(String(50), default="UPLOADED", nullable=False) # UPLOADED, PROCESSING, EXTRACTED, REVIEW_REQUIRED, APPROVED, FAILED
    extraction_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
