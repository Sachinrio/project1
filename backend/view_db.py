import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.models.schemas import Event

# Connection String
DATABASE_URL = "postgresql+asyncpg://postgres:Sankar%40722001@localhost:5432/infinitetechai"

async def view_events():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    try:
        async with async_session() as session:
        # Get Total Count
            result = await session.execute(select(Event))
            all_events = result.scalars().all()
            print(f"\nTOTAL EVENTS IN DATABASE: {len(all_events)}")
            
            print("--- LATEST 5 EVENTS ---")
            for event in all_events[-5:]:
                print(f"ID: {event.id} | Title: {event.title} | Date: {event.start_time}")
                print(f"Venue: {event.venue_name}")
                print("-" * 40)
                
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(view_events())
