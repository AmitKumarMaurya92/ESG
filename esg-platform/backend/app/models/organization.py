import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.facility import Facility
    from app.models.user import UserProfile


class Organization(Base, TimestampMixin):
    """
    Multi-tenant Organization model.
    Every enterprise user and facility belongs to an organization.
    """
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    subscription_tier: Mapped[str] = mapped_column(
        String(50),
        default="starter",
        nullable=False,
    )  # starter | pro | enterprise
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    users: Mapped[List["UserProfile"]] = relationship(
        "UserProfile",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    facilities: Mapped[List["Facility"]] = relationship(
        "Facility",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
