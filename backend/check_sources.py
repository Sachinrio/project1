
import asyncio
from sqlalchemy import text
from app.core.database import engine
async def check():
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT DISTINCT raw_data->>'source' FROM event"))
        print([r[0] for r in res])
asyncio.run(check())
