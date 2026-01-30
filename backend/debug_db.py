
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def check():
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT title, raw_data FROM event LIMIT 5"))
        for row in res.fetchall():
            print(f"TITLE: {row[0]}")
            print(f"RAW: {row[1]}")

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
