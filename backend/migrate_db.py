import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql+asyncpg://postgres:Sankar%40722001@localhost:5432/infinitetechai"

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

async def migrate():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        print("Migrating Database...")
        try:
            await conn.execute(text("ALTER TABLE event ADD COLUMN IF NOT EXISTS venue_address VARCHAR;"))
            await conn.execute(text("ALTER TABLE event ADD COLUMN IF NOT EXISTS organizer_name VARCHAR;"))
            await conn.execute(text("ALTER TABLE event ADD COLUMN IF NOT EXISTS online_event BOOLEAN DEFAULT FALSE;"))
            print("Columns added successfully!")
        except Exception as e:
            print(f"Error during migration: {e}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
