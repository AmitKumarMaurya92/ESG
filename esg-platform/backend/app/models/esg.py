import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin

class ESGMetric(Base, TimestampMixin):
    __tablename__ = "esg_metrics"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False) # Environmental, Social, Governance
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    period: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

class ESGScore(Base, TimestampMixin):
    __tablename__ = "esg_scores"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    period: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    environmental_score: Mapped[float] = mapped_column(Float, nullable=False)
    social_score: Mapped[float] = mapped_column(Float, nullable=False)
    governance_score: Mapped[float] = mapped_column(Float, nullable=False)
    methodology_version: Mapped[str] = mapped_column(String(50), nullable=False)
