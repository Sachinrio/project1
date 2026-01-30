
import asyncio
import sys

# Force proper event loop for Windows + Playwright
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from app.services.event_manager import run_full_scrape_cycle
from app.services.scraper import scrape_events_playwright
from app.models.schemas import Event
from app.core.database import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def force_scrape():
    print("STARTING COMPREHENSIVE FORCE SCRAPE...")
    
    # 1. Run the Multi-Source Scraper (EventManager handles DB update)
    await run_full_scrape_cycle()
    
    # 2. ALSO run the specific Eventbrite Scraper (since it's sometimes missed)
    print("Running Specific Eventbrite Scraper...")
    eb_events = await scrape_events_playwright("chennai")
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        for data in eb_events:
            stmt = select(Event).where(Event.eventbrite_id == data['eventbrite_id'])
            result = await session.execute(stmt)
            existing = result.scalars().first()
            if not existing:
                session.add(Event(**data))
            else:
                for key, val in data.items():
                    setattr(existing, key, val)
        await session.commit()
    
    print("FORCE SCRAPE COMPLETE.")

if __name__ == "__main__":
    asyncio.run(force_scrape())
