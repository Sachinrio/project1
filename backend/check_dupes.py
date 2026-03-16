import asyncio
from sqlalchemy import text
from app.core.database import engine

async def check():
    async with engine.connect() as conn:
        print("Checking for duplicate titles and start times...")
        stmt = text("SELECT title, start_time, count(*) FROM event GROUP BY title, start_time HAVING count(*) > 1")
        res = await conn.execute(stmt)
        rows = res.fetchall()
        if rows:
            print(f"FOUND {len(rows)} DUPLICATE GROUPS:")
            for row in rows:
                print(row)
        else:
            print("NO DUPLICATES FOUND IN DB.")

if __name__ == "__main__":
    asyncio.run(check())
