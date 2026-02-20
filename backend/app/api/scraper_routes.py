
from fastapi import APIRouter, BackgroundTasks
from app.services.event_manager import run_full_scrape_cycle

router = APIRouter()

@router.post("/refresh-events")
@router.post("/sync")
async def trigger_refresh(background_tasks: BackgroundTasks):
    """
    Triggers the FULL Multi-Source Scraper (Meetup, AllEvents, CTC, Eventbrite)
    in a FastAPI BackgroundTask. This keeps it attached to the main web worker
    so Render doesn't kill it as an orphaned subprocess.
    """
    import os
    
    # Ensure Playwright path is correct for Render
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../.."))
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(project_root, "pw-browsers")
    os.environ["PYTHONPATH"] = project_root

    print("API: Triggering scraper inside FastAPI background task...")
    
    # We define a sync wrapper to run the async cycle 
    # because BackgroundTasks sometimes have issues with complex async loops
    def run_scraper_sync():
        import asyncio
        from app.services.event_manager import run_full_scrape_cycle
        print("API [Background Worker]: Starting scrape cycle...", flush=True)
        # Create a new event loop for this thread just in case
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_full_scrape_cycle())
            print("API [Background Worker]: Scrape cycle finished.", flush=True)
        except Exception as e:
            print(f"API [Background Worker]: Scrape cycle failed with error: {e}", flush=True)
        finally:
            loop.close()

    background_tasks.add_task(run_scraper_sync)
    
    return {
        "status": "accepted",
        "message": "Full scraping cycle started in a managed background task. Check Render logs. Refresh dashboard in 2-3 minutes."
    }
