import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from playwright.async_api import async_playwright

async def minimal_test():
    print("MINIMAL TEST: Starting...")
    try:
        async with async_playwright() as p:
            print("Playwright context created.")
            browser = await p.chromium.launch(headless=True)
            print("Browser launched.")
            page = await browser.new_page()
            print("Page created. Navigating...")
            await page.goto("https://www.google.com")
            print("Navigation complete.")
            await browser.close()
            print("MINIMAL TEST: SUCCESS")
    except Exception as e:
        print(f"MINIMAL TEST FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(minimal_test())
