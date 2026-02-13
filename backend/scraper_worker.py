
import sys
print("WORKER: Starting process...", flush=True)
import asyncio
print("WORKER: Importing event_manager...", flush=True)
from app.services.event_manager import run_full_scrape_cycle
print("WORKER: Imported event_manager.", flush=True)
from app.core.database import engine

async def main():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        await run_full_scrape_cycle()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
