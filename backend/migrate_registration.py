
import asyncio
from sqlalchemy.future import select
from sqlalchemy import text
from app.core.database import engine, init_db
from app.models.schemas import SQLModel

async def add_missing_columns():
    async with engine.begin() as conn:
        print("Checking for missing columns in 'userregistration' table...")
        
        # Add confirmation_id
        try:
            await conn.execute(text("ALTER TABLE userregistration ADD COLUMN confirmation_id VARCHAR"))
            print("ADDED: confirmation_id")
        except Exception as e:
            print(f"SKIPPING: confirmation_id (likely exists) - {e}")
            
        # Add status
        try:
            await conn.execute(text("ALTER TABLE userregistration ADD COLUMN status VARCHAR DEFAULT 'PENDING'"))
            print("ADDED: status")
        except Exception as e:
            print(f"SKIPPING: status (likely exists) - {e}")

    print("Migration complete.")

if __name__ == "__main__":
    import sys
    # Fix for Windows loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    asyncio.run(add_missing_columns())
