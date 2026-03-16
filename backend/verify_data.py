import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models import Event
import asyncio

load_dotenv()

# Connection String
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql+asyncpg://postgres:Sankar%40722001@localhost:5432/infinitetechai"

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL)

async def verify_data():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        result = await session.execute(select(Event))
        events = result.scalars().all()
        
        print(f"{'ID':<15} | {'ONLINE':<8} | {'VENUE':<30} | {'ORGANIZER':<30} | {'TITLE'}")
        print("-" * 120)
        
        issues_found = 0
        for e in events:
            is_suspicious = False
            if e.venue_name == "TBD" or e.organizer_name == "Unknown Organizer":
                is_suspicious = True
                issues_found += 1
                
            status_marker = "(!)" if is_suspicious else "   "
            
            print(f"{e.eventbrite_id:<15} | {str(e.online_event):<8} | {str(e.venue_name)[:30]:<30} | {str(e.organizer_name)[:30]:<30} | {status_marker} {e.title[:40]}")

        print("-" * 120)
        print(f"Total Events: {len(events)}")
        print(f"Potential Issues: {issues_found}")

if __name__ == "__main__":
    asyncio.run(verify_data())
