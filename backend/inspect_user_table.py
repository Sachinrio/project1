import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text, inspect

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to the one we know worked/is configured if .env missing
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/infinite_bz"

# Ensure asyncpg
if DATABASE_URL and not DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async def inspect_table():
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.connect() as conn:
        print(f"Connected to: {DATABASE_URL}")
        try:
             # Get all users
            result = await conn.execute(text("SELECT id, email, full_name, first_name, last_name FROM \"user\""))
            print("Successfully queried 'user' table.")
            print("Users in database:")
            rows = result.fetchall()
            for row in rows:
                print(f"ID: {row[0]}, Email: {row[1]}, Full Name: {repr(row[2])}, First: {row[3]}, Last: {row[4]}")

            print("\n=== EVENTS WITH ORGANIZER INFO ===")
            # Get events with organizer info
            event_result = await conn.execute(text("SELECT id, title, organizer_name, organizer_email FROM event LIMIT 10"))
            event_rows = event_result.fetchall()
            for row in event_rows:
                print(f"ID: {row[0]}, Title: {row[1][:40]}..., Organizer: {repr(row[2])}, Email: {repr(row[3])}")
        except Exception as e:
            print(f"Error querying 'user' table: {e}")

    await engine.dispose()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(inspect_table())
