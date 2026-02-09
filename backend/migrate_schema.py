import asyncio
from sqlalchemy import text
from app.core.database import engine

async def migrate():
    print("Starting migration...")
    async with engine.begin() as conn:
        print("Adding ticket_class_id column...")
        await conn.execute(text("ALTER TABLE userregistration ADD COLUMN IF NOT EXISTS ticket_class_id INTEGER REFERENCES ticketclass(id);"))
        
        print("Adding raw_data column...")
        await conn.execute(text("ALTER TABLE userregistration ADD COLUMN IF NOT EXISTS raw_data JSONB DEFAULT '{}';"))
        
    print("Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate())
