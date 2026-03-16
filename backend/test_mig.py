import asyncio
from app.core.database import engine
from sqlalchemy import text

async def alter_db():
    print("Altering Phase 2 fields...")
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN bank_name VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN ifsc_code VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN bank_account_number VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN major_activity VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN nic_2_digit VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN nic_4_digit VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN nic_5_digit VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN employed_male VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN employed_female VARCHAR;"))
            await conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN employed_other VARCHAR;"))
            print("Columns added.")
        except Exception as e:
            print("Already exists or error:", e)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(alter_db())
