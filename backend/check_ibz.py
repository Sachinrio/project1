
import asyncio
import sys
from sqlalchemy import text
from app.core.database import engine

async def check():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT title, description, raw_data FROM event WHERE raw_data->>'source' = 'InfiniteBZ'"))
        for r in res:
            print(f"TITLE: {r[0]}")
            print(f"DESC: {r[1]}")
            print(f"RAW: {r[2]}")
asyncio.run(check())
