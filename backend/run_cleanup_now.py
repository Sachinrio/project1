import asyncio
import sys

# Windows Proactor Loop Logic
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from app.core.database import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.cleanup import delete_expired_events

async def main():
    print("Starting manual cleanup...")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        count = await delete_expired_events(session)
        print(f"Manual Cleanup Complete. Deleted {count} events.")

if __name__ == "__main__":
    asyncio.run(main())
