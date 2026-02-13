
import asyncio
import os
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.schemas import User, Event

# Reuse connection logic from app/core/database.py slightly modified for standalone script
import sys
# Add current directory to path so imports work
sys.path.append(os.getcwd())

# DATABASE_URL from environment or hardcoded fallback (same as in database.py)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Database URL not found in env, using default from database.py logic...")
    # Using the Render internal URL found in database.py for convenience if env is missing
    # Note: This only works if running from a machine that can access this URL (Render internal network)
    # If running locally, you might need the external URL.
    # For now, let's assume the user has the env var set or we fallback to local dev
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/infinite_bz"

# Ensure asyncpg
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

print(f"Connecting to: {DATABASE_URL}")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

async def view_data():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        # 1. Users
        print("\n--- USERS ---")
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"Total Users: {len(users)}")
        for u in users[:5]:
            print(f" - {u.id}: {u.email} ({u.full_name})")

        # 2. Events
        print("\n--- EVENTS ---")
        result = await session.execute(select(Event).limit(10))
        events = result.scalars().all()
        print(f"Showing first {len(events)} events:")
        for e in events:
            print(f" - {e.id}: {e.title} ({e.start_time})")

async def main():
    try:
        await view_data()
    except Exception as e:
        print(f"Error viewing data: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
