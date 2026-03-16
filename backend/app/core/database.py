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
import asyncio

# --- ULTIMATE RENDER SSL FIX ---
# Instead of connect_args, we modify the URL directly for asyncpg compatibility
if DATABASE_URL:
    # 1. Strip any existing SSL params to prevent conflicts
    if "?" in DATABASE_URL:
        base_url, query = DATABASE_URL.split("?", 1)
        # Filter out existing ssl params
        params = [p for p in query.split("&") if not p.startswith("ssl")]
        DATABASE_URL = base_url + ("?" + "&".join(params) if params else "")

    # 2. Apply SSL based on environment
    is_external = any(domain in DATABASE_URL for domain in ["render.com", "neon.tech", "pooler.supabase.com"])
    is_internal = "internal" in DATABASE_URL or not (".com" in DATABASE_URL or ".tech" in DATABASE_URL)
    
    if is_external and not is_internal:
        # Externally connecting to Render/Neon requires SSL
        connector = "?" if "?" not in DATABASE_URL else "&"
        DATABASE_URL += f"{connector}ssl=require"
        print("DATABASE: External connection detected. Added ssl=require to URL.")
    else:
        print("DATABASE: Internal or Local connection detected. Proceeding without forced SSL.")

# 3. Create the engine with stable pooling
engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    future=True, 
    # Reduced connect_args to minimum to avoid driver conflicts
    connect_args={"command_timeout": 60},
    pool_pre_ping=True,
    pool_recycle=1200,       # Recycle faster (20 mins)
    pool_size=5,
    max_overflow=10
)

async def test_raw_connection():
    """ Diagnostic tool to test if asyncpg can connect directly. """
    import asyncpg
    # Convert SQLAlchemy URL to asyncpg DSN
    dsn = DATABASE_URL.replace("postgresql+asyncpg://", "postgres://")
    try:
        conn = await asyncpg.connect(dsn, timeout=30)
        await conn.close()
        print("DIAGNOSTIC: Raw asyncpg connection SUCCESSFUL.")
        return True
    except Exception as e:
        print(f"DIAGNOSTIC: Raw asyncpg connection FAILED: {e}")
        return False

async def init_db():
    """ Initializes the database with robust retry logic for Render deployments. """
    import asyncio
    max_retries = 3
    retry_delay = 5 # seconds
    
    # Run diagnostic first
    print("DATABASE: Running raw driver diagnostic...")
    await test_raw_connection()
    
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