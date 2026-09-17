import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin

class Scope1Record(Base, TimestampMixin):
    __tablename__ = "scope1_records"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    facility_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False) # stationary combustion, diesel, petrol...
    activity_value: Mapped[float] = mapped_column(Float, nullable=False)
    activity_unit: Mapped[str] = mapped_column(String(50), nullable=False)
    period: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # e.g. 2026-07
    emission_factor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("emission_factors.id", ondelete="SET NULL"), nullable=True)
    co2e: Mapped[float] = mapped_column(Float, nullable=False)
    source_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)

class Scope2Record(Base, TimestampMixin):
    __tablename__ = "scope2_records"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    facility_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    activity_value: Mapped[float] = mapped_column(Float, nullable=False)
    activity_unit: Mapped[str] = mapped_column(String(50), nullable=False)
    period: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    calculation_method: Mapped[str] = mapped_column(String(50), default="location-based")
    emission_factor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("emission_factors.id", ondelete="SET NULL"), nullable=True)
    co2e: Mapped[float] = mapped_column(Float, nullable=False)
    source_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)

class Scope3Record(Base, TimestampMixin):
    __tablename__ = "scope3_records"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    facility_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), index=True, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    sub_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    activity_value: Mapped[float] = mapped_column(Float, nullable=False)
    activity_unit: Mapped[str] = mapped_column(String(50), nullable=False)
    period: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    emission_factor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("emission_factors.id", ondelete="SET NULL"), nullable=True)
    co2e: Mapped[float] = mapped_column(Float, nullable=False)
    source_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
