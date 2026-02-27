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
    # Fallback or error if not set
    print("Database URL not found, checking for platform-specific defaults...")
    if os.getenv("RENDER"):
        print("Running on Render, using internal database URL")
        DATABASE_URL = "postgresql+asyncpg://infinitetechai:g1ycmCmCWLIHQhW7lwe8di70DuDopUWj@dpg-d671ds8boq4c73asch2g-a/infinitetechai_97nv"
    else:
        print("Running locally, using localhost")
        DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/infinite_bz"
else:
    print(f"Database URL found: {DATABASE_URL[:20]}... (masked)")

# Ensure asyncpg is used
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Fix for Render/Neon SSL issues
connect_args = {}
if "render.com" in DATABASE_URL or "neon.tech" in DATABASE_URL:
    connect_args = {"ssl": "require"}

engine = create_async_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)

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