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

import ssl
import traceback

# Advanced Fix for Render/Neon SSL issues
connect_args = {}
if DATABASE_URL:
    # Render and Neon often require SSL. 
    # external URLs usually have render.com or neon.tech
    if any(domain in DATABASE_URL for domain in ["render.com", "neon.tech", "pooler.supabase.com"]):
        if "internal" not in DATABASE_URL:
            # External connection needs SSL. simplified 'True' for asyncpg
            connect_args["ssl"] = True
            print("DATABASE: SSL enabled for external connection.")
        else:
            # Internal Render URLs usually don't need SSL
            connect_args["ssl"] = False 
            print("DATABASE: Internal connection detected. SSL disabled for handshake.")

# Add command timeout specifically for asyncpg
connect_args["command_timeout"] = 60

# Create the engine with optimized pool settings
engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    future=True, 
    connect_args=connect_args,
    pool_pre_ping=True,      # Checks connection health before using
    pool_recycle=1800,       # Recycle connections every 30 mins
    pool_size=5,             # Small steady pool
    max_overflow=10,         # Allow up to 10 extra temporary connections
    pool_timeout=30          # Wait up to 30s for a connection
)

async def init_db():
    """ Initializes the database with robust retry logic for Render deployments. """
    import asyncio
    max_retries = 3
    retry_delay = 5 # seconds
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"DATABASE: Connection attempt {attempt}/{max_retries}...")
            async with engine.begin() as conn:
                # verify that tables exist
                await conn.run_sync(SQLModel.metadata.create_all)
            print("DATABASE: Initialization successful!")
            return
        except Exception as e:
            print(f"DATABASE: Initialization attempt {attempt} failed.")
            traceback.print_exc() # Show the full error in Render logs
            if attempt < max_retries:
                print(f"DATABASE: Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                print("DATABASE: All connection attempts failed. Exiting.")
                raise e

async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session