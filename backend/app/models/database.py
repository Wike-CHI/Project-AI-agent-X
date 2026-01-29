"""
Database Configuration and Models
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# Synchronous engine (for migrations, etc.)
engine = create_engine(
    settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite"),
    connect_args={"check_same_thread": False}
)

# Asynchronous engine (for async API)
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG
)

# Session factories
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency for getting async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_engine():
    """Get the async engine instance."""
    return async_engine


def get_session():
    """Get a new async session."""
    return AsyncSessionLocal()
