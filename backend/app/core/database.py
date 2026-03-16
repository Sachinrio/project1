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
    # Fallback to local postgres if not set
    print("Database URL not found, using local default...")
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/infinite_bz"
else:
    print(f"Database URL found and loaded from environment")

# Ensure asyncpg is used
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Fix for Render/Neon SSL issues
connect_args = {}
if "render.com" in DATABASE_URL or "neon.tech" in DATABASE_URL:
    connect_args = {"ssl": "require"}

engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    future=True, 
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300
)

async def init_db():
    try:
        async with engine.begin() as conn:
            # verify that tables exist
            await conn.run_sync(SQLModel.metadata.create_all)
    except Exception as e:
        if "getaddrinfo failed" in str(e):
            print("\n" + "!"*50)
            print("ERROR: Database Host not found (DNS Failure).")
            print("If you are running LOCALLY, you MUST use the EXTERNAL Database URL from Render.")
            print("The internal URL (dpg-...) only works inside the Render network.")
            print("!"*50 + "\n")
        raise e

async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session