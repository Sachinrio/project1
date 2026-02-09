import asyncio
from sqlalchemy import select, or_
from app.core.database import get_session
from app.models.schemas import Event

# The exact map from routes.py
KEYWORD_MAP = {
    "startup": ["startup", "founder", "entrepreneur", "venture", "pitch", "funding", "incubator"],
    "business": ["business", "networking", "marketing", "sales", "finance", "leadership", "management", "corporate"],
    "tech": ["tech", "software", "developer", "ai", "data", "code", "programming", "cloud", "security", "web"],
    "music": ["music", "concert", "live", "dj", "band", "festival", "performance"],
    "sports": ["sport", "cricket", "football", "run", "marathon", "yoga", "fitness", "badminton"],
    # User didn't ask for Arts, but checking it anyway
    "arts": ["art", "design", "creative", "exhibition", "gallery", "painting"] 
}

async def diagnose_categories():
    async for session in get_session():
        stmt = select(Event)
        result = await session.execute(stmt)
        events = result.scalars().all()
        
        print(f"Total Events: {len(events)}")
        
        # Invert map for easy checking: event -> [categories]
        event_categories = {event.id: [] for event in events}
        
        for category, keywords in KEYWORD_MAP.items():
            print(f"\n--- Category: {category.upper()} ---")
            count = 0
            for event in events:
                text = (event.title + " " + (event.description or "")).lower()
                if any(kw in text for kw in keywords):
                    print(f"  [MATCH] {event.title}")
                    event_categories[event.id].append(category)
                    count += 1
            if count == 0:
                print("  (No events matched)")

        # Check for Unclassified Events
        print("\n\n--- UNCLASSIFIED EVENTS ---")
        unclassified_count = 0
        for event in events:
            if not event_categories[event.id]:
                print(f"ID: {event.id} | Title: {event.title}")
                print(f"  > Desc: {event.description[:100]}...")
                unclassified_count += 1
        
        if unclassified_count == 0:
            print("  (All events classified into at least one category)")

if __name__ == "__main__":
    asyncio.run(diagnose_categories())
