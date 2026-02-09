import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# Ensure asyncpg
if DATABASE_URL and not DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async def migrate_users():
    if not DATABASE_URL:
        print("DATABASE_URL not set!")
        return

    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        print(f"Migrating 'user' table on {DATABASE_URL}...")
        try:
            # List of columns to add
            columns = [
                "first_name VARCHAR",
                "last_name VARCHAR",
                "job_title VARCHAR",
                "company VARCHAR",
                "phone VARCHAR",
                "bio TEXT",
                "profile_image VARCHAR"
            ]
            
            for col_def in columns:
                col_name = col_def.split()[0]
                sql = f'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS {col_name} {col_def.split(" ", 1)[1]};'
                print(f"Executing: {sql}")
                await conn.execute(text(sql))
            
            print("User table migration completed successfully!")
        except Exception as e:
            print(f"Error during user migration: {e}")
    
    await engine.dispose()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(migrate_users())
