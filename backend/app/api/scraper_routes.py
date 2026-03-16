
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
    
    # Use an async wrapper so FastAPI runs it natively on the main event loop
    # This prevents the "attached to a different loop" error with SQLAlchemy's async engine.
    async def run_scraper_async():
        from app.services.event_manager import run_full_scrape_cycle
        print("API [Background Worker]: Starting scrape cycle on main loop...", flush=True)
        try:
            await run_full_scrape_cycle()
            print("API [Background Worker]: Scrape cycle finished.", flush=True)
        except Exception as e:
            print(f"API [Background Worker]: Scrape cycle failed with error: {e}", flush=True)

    background_tasks.add_task(run_scraper_async)
    
    return {
        "status": "accepted",
        "message": "Full scraping cycle started in a managed background task. Check Render logs. Refresh dashboard in 2-3 minutes."
    }
