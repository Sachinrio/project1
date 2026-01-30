
import asyncio
import sys
from sqlalchemy import text
from app.core.database import engine
from app.services.scrapers.utils import is_business_event
import json

async def deep_clean():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    async with engine.begin() as conn:
        print("Starting Deep Clean of Database...")
        
        # Select all events
        res = await conn.execute(text("SELECT id, title, description FROM event"))
        events = res.fetchall()
        
        deleted = 0
        for event_id, title, description in events:
            # Re-evaluate
            temp_event = {"title": title, "description": description}
            if not is_business_event(temp_event):
                await conn.execute(text(f"DELETE FROM event WHERE id = {event_id}"))
                print(f"  [DELETED] {title}")
                deleted += 1
        
        print(f"Deep Clean Finished. Deleted {deleted} events.")

if __name__ == "__main__":
    asyncio.run(deep_clean())
