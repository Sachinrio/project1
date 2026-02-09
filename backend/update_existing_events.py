import asyncio
import sys
import os

# 1. Force proper event loop for Windows + Playwright (even if we just use requests, good practice in this codebase)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Import scraper function
from app.services.scraper import fetch_event_details_api
from app.models.schemas import Event
from app.core.database import DATABASE_URL

engine = create_async_engine(DATABASE_URL)

async def update_all_events():
    print("STARTING FULL DATABASE UPDATE...")
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        # 1. Fetch all events
        print("Fetching all events from DB...")
        result = await session.execute(select(Event))
        events = result.scalars().all()
        print(f"Found {len(events)} events in database.")

        updated_count = 0
        
        for event in events:
            print(f"Checking ID: {event.eventbrite_id} | Title: {event.title[:30]}...")
            
            # 2. Fetch fresh data from API
            if not event.eventbrite_id or event.eventbrite_id == "unknown":
                print("  Skipping (No ID)")
                continue

            api_data = fetch_event_details_api(event.eventbrite_id)
            
            if api_data:
                # 3. Update fields
                changes = []
                
                # Check Organizer
                if event.organizer_name != api_data['organizer_name']:
                    changes.append(f"Organizer: {event.organizer_name} -> {api_data['organizer_name']}")
                    event.organizer_name = api_data['organizer_name']
                
                # Check Venue is Online
                if event.online_event != api_data['online_event']:
                    changes.append(f"Online: {event.online_event} -> {api_data['online_event']}")
                    event.online_event = api_data['online_event']
                    
                # Check Venue Name
                if event.venue_name != api_data['venue_name']:
                     changes.append(f"Venue: {event.venue_name} -> {api_data['venue_name']}")
                     event.venue_name = api_data['venue_name']

                # Check Venue Address
                if event.venue_address != api_data['venue_address']:
                     event.venue_address = api_data['venue_address']

                # Check Start Time
                if event.start_time != api_data['start_time']:
                    changes.append(f"Start Time: {event.start_time} -> {api_data['start_time']}")
                    event.start_time = api_data['start_time']

                # Check End Time
                if event.end_time != api_data['end_time']:
                    changes.append(f"End Time: {event.end_time} -> {api_data['end_time']}")
                    event.end_time = api_data['end_time']

                if changes:
                    print(f"  UPDATED: {', '.join(changes)}")
                    session.add(event)
                    updated_count += 1
                else:
                    print("  No changes needed.")
            else:
                print("  Failed to fetch API data.")
                
        await session.commit()
        print("-" * 30)
        print(f"COMPLETE. Updated {updated_count} events.")

if __name__ == "__main__":
    asyncio.run(update_all_events())
