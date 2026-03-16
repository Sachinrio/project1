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
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS itr_filed VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS has_gstin VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS mobile_number VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS email VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS social_category VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS gender VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS specially_abled VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS enterprise_name VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS plant_name VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS plant_address VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS official_address VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS previous_registration VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS date_of_incorporation VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS business_commenced VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS date_of_commencement VARCHAR;"))
            print("Successfully added Phase 2 fields.")
        except Exception as e:
            print(f"FAILED or already exists: {e}")

asyncio.run(alter_db())
