from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback or error if not set
    print("Warning: DATABASE_URL not found in environment, checking for individual vars or defaults...")
    # You could construct it here if you wanted, but for now let's trust the user has set it or fail
    # Default fallback just in case, but usually better to fail if env is missing
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/infinite_bz"

# Ensure asyncpg is used
if DATABASE_URL and not DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

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