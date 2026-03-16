import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.database import DATABASE_URL, connect_args

engine = create_async_engine(DATABASE_URL, echo=True, future=True, connect_args=connect_args)

new_columns = [
    "bank_name",
    "ifsc_code",
    "bank_account_number",
    "major_activity",
    "nic_search_term",
    "nic_2_digit",
    "nic_4_digit",
    "nic_5_digit",
    "persons_employed_male",
    "persons_employed_female",
    "persons_employed_others"
]

async def alter_db():
    async with engine.begin() as conn:
        for col in new_columns:
            try:
                # PostgreSQL Syntax
                await conn.execute(text(f"ALTER TABLE msmeregistration ADD COLUMN IF NOT EXISTS {col} VARCHAR;"))
                print(f"Column {col} ADDED")
            except Exception as e:
                print(f"FAILED or already exists for {col}: {e}")
                try:
                    # SQLite syntax fallback
                    await conn.execute(text(f"ALTER TABLE msmeregistration ADD COLUMN {col} VARCHAR;"))
                    print(f"Column {col} ADDED via fallback")
                except Exception as e2:
                    print(f"Fallback FAILED for {col}: {e2}")

asyncio.run(alter_db())
