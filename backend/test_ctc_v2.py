
import asyncio
from playwright.async_api import async_playwright
from app.services.scrapers.trade_centre import CTCScraper
import sys

async def test():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        scraper = CTCScraper()
        print("Starting CTC Scrape...")
        events = await scraper.scrape(page)
        print(f"Collected {len(events)} events.")
        for e in events[:5]:
            print(f" - {e['title']} | Date: {e['start_time']}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test())
