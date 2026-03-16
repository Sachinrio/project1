import os
from dotenv import load_dotenv

load_dotenv()

# Hardcoded from your config
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql+asyncpg://postgres:Sankar%40722001@localhost:5432/infinitetechai"

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL)

async def seed():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        print("SEEDING: Creating dummy event...")
        event = Event(
            eventbrite_id="TEST_123",
            title="Test Event: AI & Future",
            description="A generic test event.",
            start_time=datetime.now(),
            end_time=datetime.now(),
            url="https://google.com",
            venue_name="Virtual Tech Hub",
            is_free=True,
            raw_data={}
        )
        try:
            session.add(event)
            await session.commit()
            print("✅ SEED SUCCESS! One event added.")
        except Exception as e:
            print(f"SEED FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(seed())
