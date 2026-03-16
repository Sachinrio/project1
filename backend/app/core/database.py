from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import os
from dotenv import load_dotenv

# Import schemas to ensure they are registered with SQLModel before metadata.create_all runs
from app.models.schemas import *
from app.models.msme_schema import MSMERegistration, ChatSession

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("CRITICAL: DATABASE_URL not found in environment variables!")
    # No more hardcoded fallbacks to prevent accidental connections to stale databases
    raise ValueError("DATABASE_URL is not set. Please check your environment variables.")
else:
    print(f"DATABASE STARTUP: Using URL starting with {DATABASE_URL[:20]}...")

# Ensure asyncpg is used
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Fix for Render/Neon SSL issues
connect_args = {}
# Only require SSL for external connections to Render/Neon
if "render.com" in DATABASE_URL or "neon.tech" in DATABASE_URL:
    if "internal" not in DATABASE_URL:
        connect_args["ssl"] = "require"
        print("DATABASE: SSL required for external connection.")

engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    future=True, 
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300
)

async def init_db():
    async with engine.begin() as conn:
        # verify that tables exist
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session