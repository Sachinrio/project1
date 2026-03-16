import asyncio
from sqlalchemy import text
from app.core.database import engine

async def reset_tables():
    async with engine.begin() as conn:
        print("🗑️  Deleting old tables...")
        # We use CASCADE to remove everything linked to these tables
        await conn.execute(text("DROP TABLE IF EXISTS userregistration CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS event CASCADE;"))
        print("✅ Tables deleted successfully!")
        print("🚀 Now restart your server (uvicorn) to recreate them automatically.")

if __name__ == "__main__":
    asyncio.run(reset_tables())