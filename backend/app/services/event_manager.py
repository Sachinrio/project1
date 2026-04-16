
import asyncio
from sqlalchemy import delete
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.database import engine
from app.models.schemas import Event

# Import Scrapers
print("EVENT MANAGER: Importing scrapers...", flush=True)
from app.services.scrapers.meetup import MeetupScraper
from app.services.scrapers.allevents import AllEventsScraper
from app.services.scrapers.trade_centre import CTCScraper
from app.services.scraper import scrape_events_playwright # Eventbrite Scraper
from playwright.async_api import async_playwright
print("EVENT MANAGER: Scrapers imported.", flush=True)

async def run_full_scrape_cycle():
    """
    Orchestrator that runs all scrapers and updates DB.
    """
    print("EVENT MANAGER: Starting Full Scrape Cycle...")
    
    async def run_playwright_scraper(scraper_class):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
                )
                page = await browser.new_page()
                
                # Block heavy assets to prevent OOM
                async def route_handler(route):
                    if route.request.resource_type in ["image", "media", "font"]:
                        await route.abort()
                    else:
                        await route.continue_()
                await page.route("**/*", route_handler)
                
                scraper = scraper_class()
                events = await scraper.scrape(page)
                await browser.close()
                return events
        except Exception as e:
            print(f"{scraper_class.__name__} Error: {e}")
            return []

    # Run sequentially to prevent Out of Memory (OOM) crashes on Render
    try:
        print("EVENT MANAGER: Launching Meetup Scraper (1/4)...", flush=True)
        meetup_events = await run_playwright_scraper(MeetupScraper)
        print(f"EVENT MANAGER: Meetup finished! Found {len(meetup_events)} events.", flush=True)
    except Exception as e:
        print(f"EVENT MANAGER: Meetup failed: {e}", flush=True)
        meetup_events = []
        
    try:
        print("\nEVENT MANAGER: Launching AllEvents Scraper (2/4)...", flush=True)
        allevents = await run_playwright_scraper(AllEventsScraper)
        print(f"EVENT MANAGER: AllEvents finished! Found {len(allevents)} events.", flush=True)
    except Exception as e:
        print(f"EVENT MANAGER: AllEvents failed: {e}", flush=True)
        allevents = []
        
    try:
        print("\nEVENT MANAGER: Launching CTC Scraper (3/4)...", flush=True)
        ctc_events = await run_playwright_scraper(CTCScraper)
        print(f"EVENT MANAGER: CTC finished! Found {len(ctc_events)} events.", flush=True)
    except Exception as e:
        print(f"EVENT MANAGER: CTC failed: {e}", flush=True)
        ctc_events = []
        
    try:
        print("\nEVENT MANAGER: Launching Eventbrite Scraper (4/4)...", flush=True)
        eb_events = await scrape_events_playwright("chennai")
        print(f"EVENT MANAGER: Eventbrite finished! Found {len(eb_events)} events.", flush=True)
    except Exception as e:
        print(f"EVENT MANAGER: Eventbrite failed: {e}", flush=True)
        eb_events = []

    results = [meetup_events, allevents, ctc_events, eb_events]
    all_new_events = []
    for res in results:
        all_new_events.extend(res)

    print(f"EVENT MANAGER: Scraped {len(all_new_events)} total events.")
    
    # 2. Save to Database
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        added = 0
        updated = 0
        for data in all_new_events:
            stmt = select(Event).where(Event.eventbrite_id == data['eventbrite_id'])
            result = await session.execute(stmt)
            existing = result.scalars().first()
            
            if not existing:
                event = Event(**data)
                session.add(event)
                added += 1
            else:
                # Comprehensive Update Logic
                existing.title = data['title']
                existing.description = data['description']
                existing.start_time = data['start_time']
                existing.end_time = data['end_time']
                existing.venue_name = data['venue_name']
                existing.venue_address = data.get('venue_address')
                existing.organizer_name = data.get('organizer_name')
                existing.image_url = data.get('image_url')
                existing.is_free = data.get('is_free', False)
                existing.online_event = data.get('online_event', False)
                existing.url = data['url']
                existing.raw_data = data.get('raw_data', {})
                updated += 1
        
        await session.commit()
        print(f"EVENT MANAGER: DB Saved {added} new, Updated {updated}.")
        
        # 3. Cleanup Old Events
        await remove_outdated_events(session)

# Import UserRegistration to handle foreign key cleanup
from app.models.schemas import Event, UserRegistration, TicketClass

# ... (Previous imports remain same) ...

# ... (scrapers import) ...

# ... (run_full_scrape_cycle function) ...

async def remove_outdated_events(session: AsyncSession):
    """
    Deletes events where end_time < NOW.
    Safely handles foreign keys by deleting related registrations first.
    """
    try:
        current_time = datetime.now()
        # print(f"CLEANUP: Checking for events older than {current_time}...")
        
        # 1. Select IDs of events to delete
        stmt_select = select(Event.id).where(Event.end_time < current_time)
        result_ids = await session.execute(stmt_select)
        event_ids = result_ids.scalars().all()
        
        if not event_ids:
            # print("CLEANUP: No old events found.")
            return

        print(f"CLEANUP: Found {len(event_ids)} old events to delete.")

        # 2. Delete related registrations first
        stmt_del_regs = delete(UserRegistration).where(UserRegistration.event_id.in_(event_ids))
        res_regs = await session.execute(stmt_del_regs)
        print(f"CLEANUP: Deleted {res_regs.rowcount} related registrations.")

        # 3. Delete related ticket classes
        stmt_del_tickets = delete(TicketClass).where(TicketClass.event_id.in_(event_ids))
        res_tickets = await session.execute(stmt_del_tickets)
        print(f"CLEANUP: Deleted {res_tickets.rowcount} related ticket classes.")

        # 4. Delete events
        stmt_del_events = delete(Event).where(Event.id.in_(event_ids))
        res_events = await session.execute(stmt_del_events)
        await session.commit()
        
        print(f"CLEANUP: Deleted {res_events.rowcount} old events.")
    except Exception as e:
        print(f"CLEANUP FAILED: {e}")
        # Rollback in case of error to keep DB consistent
        await session.rollback()
