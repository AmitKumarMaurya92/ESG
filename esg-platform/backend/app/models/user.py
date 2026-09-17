import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String
from app.db.types import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.organization import Organization


class UserProfile(Base, TimestampMixin):
    """
    User Profile extending Supabase Auth user record.
    Stores application-specific role and multi-tenant organization association.
    """
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        comment="Matches Supabase auth.users.id",
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        default="EMPLOYEE",
        nullable=False,
    )  # SUPER_ADMIN, ORGANIZATION_ADMIN, SUSTAINABILITY_MANAGER, COMPLIANCE_OFFICER, AUDITOR, SUPPLIER, EMPLOYEE
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        back_populates="users",
    )

