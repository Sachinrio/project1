
import asyncio
import sys
from sqlalchemy import text
from app.core.database import engine

async def audit_titles():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    async with engine.begin() as conn:
        print("--- Stored Event Titles ---")
        res = await conn.execute(text("SELECT title, raw_data->>'source' as src FROM event ORDER BY src LIMIT 50"))
        for row in res:
            print(f"[{row[1]}] {row[0]}")

if __name__ == "__main__":
    asyncio.run(audit_titles())
