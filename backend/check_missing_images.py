
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def check():
    async with engine.begin() as conn:
        print("--- Eventbrite ---")
        res = await conn.execute(text("SELECT title, image_url FROM event WHERE raw_data->>'source' = 'eventbrite' AND (image_url IS NULL OR image_url = '') LIMIT 5"))
        for row in res.fetchall():
            print(f"TITLE: {row[0]} | IMG: {row[1]}")
            
        print("\n--- AllEvents ---")
        res = await conn.execute(text("SELECT title, image_url FROM event WHERE raw_data->>'source' = 'allevents' AND (image_url IS NULL OR image_url = '') LIMIT 5"))
        for row in res.fetchall():
            print(f"TITLE: {row[0]} | IMG: {row[1]}")
            
        print("\n--- Samples with URLs (Check if they look valid) ---")
        res = await conn.execute(text("SELECT raw_data->>'source', image_url FROM event WHERE image_url IS NOT NULL AND image_url != '' LIMIT 10"))
        for row in res.fetchall():
            print(f"SRC: {row[0]} | URL: {row[1][:100]}...")

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(check())
    finally:
        loop.close()
