import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.database import DATABASE_URL, connect_args

engine = create_async_engine(DATABASE_URL, echo=True, future=True, connect_args=connect_args)

async def alter_db():
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS otp_code VARCHAR;"))
            print("Column ADDED")
        except Exception as e:
            print(f"FAILED or already exists: {e}")
            try:
                # SQLite syntax fallback
                await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN otp_code VARCHAR;"))
                print("Column ADDED via fallback")
            except Exception as e2:
                print(f"Fallback FAILED: {e2}")

asyncio.run(alter_db())
