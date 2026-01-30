
import asyncio
import sys
from playwright.async_api import async_playwright
from app.services.scrapers.allevents import AllEventsScraper

async def test():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        scraper = AllEventsScraper()
        print("Starting test scrape...")
        events = await scraper.scrape(page)
        print(f"Scraped {len(events)} events.")
        for i, ev in enumerate(events[:5]):
            print(f"[{i}] {ev['title'][:30]} -> {ev['image_url']}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test())
