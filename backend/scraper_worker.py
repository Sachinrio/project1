
import asyncio
import sys
from app.services.event_manager import run_full_scrape_cycle
from app.core.database import engine

async def main():
    # SELF-HEALING: Ensure browsers are installed
    # This fixes the "Executable doesn't exist" error even if build command failed
    import subprocess
    print("Scraper Worker: Checking/Installing Playwright Browsers...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    except Exception as e:
        print(f"Scraper Worker: Warning - Browser install failed: {e}")

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        await run_full_scrape_cycle()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
