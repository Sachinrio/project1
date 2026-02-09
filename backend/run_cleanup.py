import asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import engine
from app.services.cleanup import delete_expired_events

async def main():
    print("Starting cleanup of past events...")
    
    # Create the session factory
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            deleted_count = await delete_expired_events(session)
            print(f"Successfully deleted {deleted_count} past events.")
        except Exception as e:
            print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    asyncio.run(main())
