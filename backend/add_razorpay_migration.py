import asyncio
from sqlalchemy import text
from app.core.database import get_session, engine

async def add_razorpay_column():
    async with engine.begin() as conn:
        print("Checking for razorpay_account_id column...")
        try:
            # Check if column exists
            cmd = text("SELECT razorpay_account_id FROM user LIMIT 1")
            await conn.execute(cmd)
            print("Column 'razorpay_account_id' already exists. Skipping.")
        except Exception:
            print("Column not found. Adding 'razorpay_account_id' to 'user' table...")
            # SQLite does not support IF NOT EXISTS in ADD COLUMN usually, but try catch handles it
            # For SQLite: ALTER TABLE user ADD COLUMN razorpay_account_id TEXT;
            # For Postgres: ALTER TABLE "user" ADD COLUMN razorpay_account_id VARCHAR;
            
            # Assuming SQLite based on previous context, but generic SQL matches simple types
            try:
                # user is a reserved word in PG, so quote it if using PG, but SQLModel generic might vary.
                # The table name in schema is likely 'user' (lowercase) by default in SQLModel
                await conn.execute(text("ALTER TABLE user ADD COLUMN razorpay_account_id VARCHAR"))
                print("Column added successfully.")
            except Exception as e:
                print(f"Failed to add column (might differ by DB type): {e}")

if __name__ == "__main__":
    asyncio.run(add_razorpay_column())
