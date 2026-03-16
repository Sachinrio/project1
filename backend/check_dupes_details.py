
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def check_details():
    async with engine.connect() as conn:
        print("Checking duplicate details for 'GLOBAL STARTUPS CLUB'...")
        # Using simple query to avoid complex raw_data access issues initially
        stmt = text("SELECT id, title, eventbrite_id, start_time FROM event WHERE title LIKE 'GLOBAL STARTUPS CLUB%'")
        res = await conn.execute(stmt)
        rows = res.fetchall()
        for row in rows:
            print(row)

if __name__ == "__main__":
    asyncio.run(check_details())
