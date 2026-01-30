
import asyncio
import sys
from playwright.async_api import async_playwright
from app.services.scrapers.allevents import AllEventsScraper
from app.core.database import engine
from app.models.schemas import Event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def fix():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        scraper = AllEventsScraper()
        print("Starting Surgical AllEvents Scrape...")
        events = await scraper.scrape(page)
        print(f"Scraped {len(events)} events.")
        
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            updated = 0
            for data in events:
                stmt = select(Event).where(Event.eventbrite_id == data['eventbrite_id'])
                result = await session.execute(stmt)
                existing = result.scalars().first()
                if existing:
                    print(f"Updating ID {existing.id}: {data['image_url'][:50]}...")
                    existing.image_url = data['image_url']
                    updated += 1
            await session.commit()
            print(f"DONE. Updated {updated} events.")
        await browser.close()

if __name__ == "__main__":
    try:
        asyncio.run(fix())
    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
