import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String
from app.db.types import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.organization import Organization


class Facility(Base, TimestampMixin):
    """
    Facility model representing enterprise operational sites.
    All carbon emission calculations are tagged by facility and organization.
    """
    __tablename__ = "facilities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    state_province: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    facility_type: Mapped[str] = mapped_column(
        String(100),
        default="office",
        nullable=False,
    )  # office | manufacturing | warehouse | data_center | retail
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="facilities",
    )


