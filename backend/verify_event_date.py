
import asyncio
from sqlmodel import select
from app.core.database import get_session
from app.models.schemas import Event

async def check_event():
    async for session in get_session():
        # Search for "Train The Trainer"
        statement = select(Event).where(Event.title.ilike("%Train The Trainer%"))
        result = await session.execute(statement)
        events = result.scalars().all()
        
        print(f"Found {len(events)} events matching 'Train The Trainer'.")
        
        for event in events:
            print(f"--- Event ID: {event.id} ---")
            print(f"Title: {event.title}")
            print(f"Start Time: {event.start_time}")
            print(f"End Time: {event.end_time}")
            print(f"Eventbrite ID: {event.eventbrite_id}")
            print(f"URL: {event.url}")
            print("-----------------------------")

if __name__ == "__main__":
    asyncio.run(check_event())
