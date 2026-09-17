"""
Custom SQLAlchemy types that work across PostgreSQL (production) and SQLite (local dev).
"""
import uuid as _uuid_mod

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator


class UUID(TypeDecorator):
    """
    Platform-independent UUID type.
    - PostgreSQL: uses native UUID column type.
    - SQLite / other: stores as a VARCHAR(36).
    """

    impl = String
    cache_ok = True

    def __init__(self, as_uuid: bool = True, *args, **kwargs):
        self.as_uuid = as_uuid
        super().__init__(36, *args, **kwargs)

    def load_dialect_impl(self, dialect: Dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=self.as_uuid))
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value  # handled natively
        if isinstance(value, _uuid_mod.UUID):
            return str(value)
        # Accept raw string UUIDs
        return str(_uuid_mod.UUID(str(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if not self.as_uuid:
            return str(value)
        if isinstance(value, _uuid_mod.UUID):
            return value
        return _uuid_mod.UUID(str(value))
