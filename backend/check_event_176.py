import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from app.core.database import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.schemas import Event
from sqlalchemy import select

async def main():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        result = await session.execute(select(Event).where(Event.id == 176))
        event = result.scalars().first()
        if event:
            print(f"Event 176 Title: {event.title}")
            print(f"raw_data source: {event.raw_data.get('source') if event.raw_data else 'None'}")
            print(f"organizer: {event.organizer_name}")
            print(f"is_internal bool: {event.raw_data.get('source') == 'InfiniteBZ' if event.raw_data else 'None'}")
        else:
            print("Event 176 not found.")

if __name__ == "__main__":
    asyncio.run(main())
