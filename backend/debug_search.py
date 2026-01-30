
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def check():
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT title, raw_data->>'source' FROM event WHERE title ILIKE '%Chennai Tech%'"))
        rows = res.fetchall()
        print(f"FOUND {len(rows)} matching events")
        for row in rows:
            print(f"TITLE: {row[0]} | SRC: {row[1]}")

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
