import sys
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.database import DATABASE_URL, connect_args

engine = create_async_engine(DATABASE_URL, echo=True, future=True, connect_args=connect_args)

async def alter_db():
    print("Migrating schema to PostgreSQL (Phase 5)...")
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS nic_activity_type VARCHAR;"))
            print("Successfully added nic_activity_type field.")
        except Exception as e:
            print(f"FAILED or already exists: {e}")

if __name__ == "__main__":
    asyncio.run(alter_db())
