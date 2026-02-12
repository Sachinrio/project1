import asyncio
import sys
from playwright.async_api import async_playwright
from app.services.scrapers.trade_centre import CTCScraper

async def test_ctc_scraper():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    print("Initializing Playwright...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        scraper = CTCScraper()
        
        print("Running CTC Scraper...")
        events = await scraper.scrape(page)
        
        print(f"\n--- Results ({len(events)} events found) ---")
        for event in events:
            print(f"- {event['title']}")
            print(f"  Start: {event['start_time']}")
            print(f"  URL: {event['url']}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_ctc_scraper())
