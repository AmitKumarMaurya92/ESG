"""
Model registry — import every SQLAlchemy model here so Alembic autogenerate
can see them all.
"""

from app.db.base_class import Base  # noqa: F401
from app.models.base import TimestampMixin  # noqa: F401
from app.models.organization import Organization  # noqa: F401
from app.models.user import UserProfile  # noqa: F401
from app.models.facility import Facility  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.emission_factor import EmissionFactor  # noqa: F401
from app.models.emission import Scope1Record, Scope2Record, Scope3Record  # noqa: F401
from app.models.esg import ESGMetric, ESGScore  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.risk import RiskEvent  # noqa: F401
from app.models.compliance import Framework, FrameworkRequirement, ComplianceRecord  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.report import Report  # noqa: F401
from app.models.supplier import Supplier  # noqa: F401
