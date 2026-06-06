"""
Database Session Management
Async SQLAlchemy session for Supabase PostgreSQL
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config.settings import get_settings

settings = get_settings()

# Create async engine
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")
engine_kwargs = {"pool_size": 10, "max_overflow": 20}
if _is_sqlite:
    engine_kwargs = {"connect_args": {"check_same_thread": False}}
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=not _is_sqlite,
    **engine_kwargs,
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
