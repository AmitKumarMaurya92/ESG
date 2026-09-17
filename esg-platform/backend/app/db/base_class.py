from typing import Any

from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """
    SQLAlchemy 2.0 Declarative Base.
    All models will inherit from this class.
    """
    id: Any
    
    # Generate __tablename__ automatically
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
