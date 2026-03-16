import sys
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.database import DATABASE_URL, connect_args

engine = create_async_engine(DATABASE_URL, echo=True, future=True, connect_args=connect_args)

async def alter_db():
    print("Migrating schema to PostgreSQL...")
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS major_activity_under_services VARCHAR;"))
            print("Successfully added major_activity_under_services field.")
        except Exception as e:
            print(f"FAILED or already exists: {e}")

if __name__ == "__main__":
    asyncio.run(alter_db())
