
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def add_missing_columns():
    async with engine.begin() as conn:
        print("Checking for missing columns in 'userregistration' table...")
        
        # Add checked_in_at
        try:
            # Using TIMESTAMP for datetime
            await conn.execute(text("ALTER TABLE userregistration ADD COLUMN checked_in_at TIMESTAMP WITHOUT TIME ZONE"))
            print("ADDED: checked_in_at")
        except Exception as e:
            print(f"SKIPPING: checked_in_at (likely exists or other error) - {e}")
            
    print("Migration complete.")

if __name__ == "__main__":
    import sys
    # Fix for Windows loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    asyncio.run(add_missing_columns())
