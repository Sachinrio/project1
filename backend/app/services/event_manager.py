"""
Event Manager — Orchestrates all scrapers and saves results to DB.
ALL scrapers are now HTTP-only (no Playwright/Chromium).
This is required for Render's free tier (512MB RAM).
"""

import asyncio
from sqlalchemy import delete
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.database import engine
from app.models.schemas import Event

# Import HTTP-only Scrapers
print("EVENT MANAGER: Importing scrapers...", flush=True)
from app.services.scrapers.meetup import MeetupScraper
from app.services.scrapers.allevents import AllEventsScraper
from app.services.scrapers.trade_centre import CTCScraper
from app.services.scraper import scrape_events_playwright   # Eventbrite (HTTP)
print("EVENT MANAGER: Scrapers imported.", flush=True)


async def _run_scraper_safe(name: str, coro) -> list:
    """Runs a scraper coroutine with a timeout and error guard."""
    print(f"EVENT MANAGER: Starting {name}...", flush=True)
    try:
        result = await asyncio.wait_for(coro, timeout=120)  # 2-min max per scraper
        print(f"EVENT MANAGER: {name} finished. Found {len(result)} events.", flush=True)
        return result
    except asyncio.TimeoutError:
        print(f"EVENT MANAGER: {name} timed out after 2 minutes.", flush=True)
        return []
    except Exception as e:
        print(f"EVENT MANAGER: {name} failed: {e}", flush=True)
        return []


async def run_full_scrape_cycle():
    """
    Orchestrator: runs all HTTP scrapers sequentially and saves results to DB.
    No Playwright/Chromium is spawned at all — safe for Render free tier.
    """
    print("EVENT MANAGER: Starting Full Scrape Cycle (HTTP-only mode)...", flush=True)

    meetup_scraper = MeetupScraper()
    allevents_scraper = AllEventsScraper()
    ctc_scraper = CTCScraper()

    # Run sequentially (small delay between each to avoid hammering Render's network)
    meetup_events = await _run_scraper_safe("Meetup (1/4)", meetup_scraper.scrape_http())
    await asyncio.sleep(1)

    allevents_events = await _run_scraper_safe("AllEvents (2/4)", allevents_scraper.scrape_http())
    await asyncio.sleep(1)

    ctc_events = await _run_scraper_safe("CTC (3/4)", ctc_scraper.scrape_http())
    await asyncio.sleep(1)

    eb_events = await _run_scraper_safe("Eventbrite (4/4)", scrape_events_playwright("chennai"))

    all_new_events = meetup_events + allevents_events + ctc_events + eb_events
    print(f"EVENT MANAGER: Total scraped: {len(all_new_events)} events.", flush=True)

    if not all_new_events:
        print("EVENT MANAGER: No events scraped. Skipping DB update.", flush=True)
        return

    # Save to Database
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        added = 0
        updated = 0
        for data in all_new_events:
            try:
                stmt = select(Event).where(Event.eventbrite_id == data["eventbrite_id"])
                result = await session.execute(stmt)
                existing = result.scalars().first()

                if not existing:
                    event = Event(**data)
                    session.add(event)
                    added += 1
                else:
                    existing.title = data["title"]
                    existing.description = data["description"]
                    existing.start_time = data["start_time"]
                    existing.end_time = data["end_time"]
                    existing.venue_name = data["venue_name"]
                    existing.venue_address = data.get("venue_address")
                    existing.organizer_name = data.get("organizer_name")
                    existing.image_url = data.get("image_url")
                    existing.is_free = data.get("is_free", False)
                    existing.online_event = data.get("online_event", False)
                    existing.url = data["url"]
                    existing.raw_data = data.get("raw_data", {})
                    updated += 1
            except Exception as e:
                print(f"EVENT MANAGER: DB save error for '{data.get('title')}': {e}")
                continue

        await session.commit()
        print(f"EVENT MANAGER: DB Saved {added} new, Updated {updated}.", flush=True)

        # Cleanup outdated events
        await remove_outdated_events(session)


# Import models for FK cleanup
from app.models.schemas import Event, UserRegistration, TicketClass


async def remove_outdated_events(session: AsyncSession):
    """
    Deletes events where end_time < NOW.
    Safely handles foreign keys by deleting related records first.
    """
    try:
        current_time = datetime.now()

        stmt_select = select(Event.id).where(Event.end_time < current_time)
        result_ids = await session.execute(stmt_select)
        event_ids = result_ids.scalars().all()

        if not event_ids:
            return

        print(f"CLEANUP: Found {len(event_ids)} old events to delete.")

        stmt_del_regs = delete(UserRegistration).where(UserRegistration.event_id.in_(event_ids))
        res_regs = await session.execute(stmt_del_regs)
        print(f"CLEANUP: Deleted {res_regs.rowcount} registrations.")

        stmt_del_tickets = delete(TicketClass).where(TicketClass.event_id.in_(event_ids))
        res_tickets = await session.execute(stmt_del_tickets)
        print(f"CLEANUP: Deleted {res_tickets.rowcount} ticket classes.")

        stmt_del_events = delete(Event).where(Event.id.in_(event_ids))
        res_events = await session.execute(stmt_del_events)
        await session.commit()

        print(f"CLEANUP: Deleted {res_events.rowcount} old events.")
    except Exception as e:
        print(f"CLEANUP FAILED: {e}")
        await session.rollback()
