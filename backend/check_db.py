import asyncio
from sqlalchemy import text
from app.core.database import engine

import sys

# Windows Loop Policy Fix
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def check_schema():
    print("Checking Schema...")
    async with engine.begin() as conn:
        try:
            # Try selecting the column
            await conn.execute(text("SELECT razorpay_account_id FROM user LIMIT 1"))
            print("SUCCESS: Column 'razorpay_account_id' exists.")
        except Exception as e:
            print(f"INFO: Column missing or other error: {e}")
            print("Attempting to add column...")
            try:
                # Try adding it
                await conn.execute(text("ALTER TABLE user ADD COLUMN razorpay_account_id VARCHAR"))
                print("SUCCESS: Column added.")
            except Exception as e2:
                print(f"ERROR: Failed to add column: {e2}")

if __name__ == "__main__":
    try:
        asyncio.run(check_schema())
    except Exception as e:
        print(f"CRITICAL FAULT: {e}")
