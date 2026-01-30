
import asyncio
from playwright.async_api import async_playwright
import sys

async def debug():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Use simple URL first
        print("Navigating to AllEvents...")
        try:
            await page.goto("https://allevents.in/chennai/all", timeout=60000)
            await page.wait_for_selector('body', timeout=20000)
            # wait a bit for lazy-load
            await asyncio.sleep(5)
            content = await page.content()
            with open("ae_debug.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("Saved ae_debug.html")
        except Exception as e:
            print(f"Error: {e}")
            await page.screenshot(path="ae_error.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug())
