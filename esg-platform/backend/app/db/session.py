import logging

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

# Fallback to in-memory SQLite if no DATABASE_URL is provided yet,
# so the app doesn't crash on startup during early phases.
DB_URL = settings.DATABASE_URL
if not DB_URL:
    logger.warning("DATABASE_URL is missing. Using local SQLite file for now.")
    DB_URL = "sqlite+aiosqlite:///./esg_local.db"
elif DB_URL.startswith("postgres://"):
    # SQLAlchemy requires `postgresql+asyncpg://`
    DB_URL = DB_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DB_URL.startswith("postgresql://"):
    DB_URL = DB_URL.replace("postgresql://", "postgresql+asyncpg://", 1)


engine = create_async_engine(
    DB_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db():
    """
    Dependency to yield an async database session per request.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
