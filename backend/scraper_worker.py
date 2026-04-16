"""
Standalone scraper worker — called by scheduler or manually.
HTTP-only: no Playwright/Chromium spawned.
"""

import sys
print("WORKER: Starting process...", flush=True)
import asyncio
print("WORKER: Importing event_manager...", flush=True)
from app.services.event_manager import run_full_scrape_cycle
print("WORKER: Imported event_manager.", flush=True)
from app.core.database import engine

async def main():
    import os
    print(f"WORKER: PYTHONPATH={os.environ.get('PYTHONPATH')}", flush=True)
    print(f"WORKER: CWD={os.getcwd()}", flush=True)

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        print("WORKER: Starting HTTP scrape cycle...", flush=True)
        await run_full_scrape_cycle()
        print("WORKER: Scrape cycle finished successfully.", flush=True)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
