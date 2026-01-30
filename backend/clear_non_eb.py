
import asyncio
from sqlalchemy import text
from app.core.database import engine
async def delete():
    async with engine.begin() as conn:
        res = await conn.execute(text("DELETE FROM event WHERE raw_data->>'source' IN ('allevents', 'trade_centre', 'meetup')"))
        print(f"Deleted {res.rowcount} events.")
asyncio.run(delete())
