
import asyncio
from playwright.async_api import async_playwright
from app.services.scrapers.allevents import AllEventsScraper
import sys

async def test():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        scraper = AllEventsScraper()
        print("Starting AllEvents Scrape...")
        events = await scraper.scrape(page)
        print(f"Collected {len(events)} events.")
        for e in events[:5]:
            print(f" - {e['title']} | IMG: {e['image_url'][:50]}...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test())
