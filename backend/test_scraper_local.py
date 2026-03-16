import asyncio
import os
from app.services.scraper import scrape_events_playwright
from dotenv import load_dotenv

load_dotenv()

# Force Render DB just in case saving works, though we mainly want to see the output list
# os.environ["DATABASE_URL"] = "postgresql+asyncpg://..." # Already in .env

async def test_scraper():
    print("Starting Local Scraper Test...")
    try:
        events = await scrape_events_playwright(city="chennai", category="business")
        print(f"Scraper returned {len(events)} events.")
        for e in events:
            print(f" - Found: {e['title']} | {e['venue_address']}")
    except Exception as e:
        print(f"Scraper Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_scraper())
