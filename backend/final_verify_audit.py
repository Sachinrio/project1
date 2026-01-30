
import asyncio
import sys
from sqlalchemy import text
from app.core.database import engine

async def audit():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    async with engine.begin() as conn:
        print("--- Source Counts ---")
        res = await conn.execute(text("SELECT raw_data->>'source' as src, count(*) FROM event GROUP BY 1"))
        for row in res:
            print(f"{row[0]}: {row[1]}")
            
        print("\n--- Image Quality Audit (AllEvents) ---")
        res = await conn.execute(text("SELECT count(*) FROM event WHERE image_url LIKE '%og-logo%'"))
        print(f"Generic Logos (og-logo): {res.scalar()}")
        
        res = await conn.execute(text("SELECT count(*) FROM event WHERE image_url LIKE '%cdn-ip.allevents.in%'"))
        print(f"High Quality (cdn-ip): {res.scalar()}")
        
        print("\n--- Sample Images (Eventbrite) ---")
        res = await conn.execute(text("SELECT image_url FROM event WHERE raw_data->>'source' = 'eventbrite_api' LIMIT 5"))
        for row in res:
            print(f"EB IMG: {row[0]}")

if __name__ == "__main__":
    asyncio.run(audit())
