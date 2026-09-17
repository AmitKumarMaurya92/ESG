import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Float, String, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.base import TimestampMixin

class EmissionFactor(Base, TimestampMixin):
    __tablename__ = "emission_factors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    scope: Mapped[int] = mapped_column(nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    factor: Mapped[float] = mapped_column(Float, nullable=False)
    co2_factor: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ch4_factor: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    n2o_factor: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    valid_from: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    valid_to: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    methodology: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
