import asyncio
import sys
from playwright.async_api import async_playwright
from app.services.scrapers.meetup import MeetupScraper

async def test_meetup_scraper():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    print("Initializing Playwright...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        scraper = MeetupScraper()
        
        print("Running Meetup Scraper...")
        events = await scraper.scrape(page)
        
        print(f"\n--- Results ({len(events)} events found) ---")
        for event in events:
            print(f"- {event['title']} ({event['start_time']})")
            print(f"  URL: {event['url']}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_meetup_scraper())
