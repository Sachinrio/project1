
from fastapi import APIRouter, BackgroundTasks
from app.services.event_manager import run_full_scrape_cycle

router = APIRouter()

@router.post("/refresh-events")
@router.post("/sync")
async def trigger_refresh():
    """
    Triggers the FULL Multi-Source Scraper (Meetup, AllEvents, CTC, Eventbrite)
    in a background process (subprocess) with proper environment for Render.
    """
    import subprocess
    import sys
    import os
    
    # Path to the virtualenv python
    python_exe = sys.executable
    
    # LOCATE WORKER SCRIPT RELATIVE TO THIS FILE
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../..")) # Go up 2 levels: api -> app -> backend
    
    worker_script = os.path.join(project_root, "scraper_worker.py")
    
    # Pass current environment + PYTHONPATH to ensure imports work
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root # CRITICAL: Ensure backend root is in python path
    
    # Point Playwright to the local browser folder created by build.sh
    # project_root is .../backend
    env["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(project_root, "pw-browsers")
    
    print(f"API: Triggering worker at {worker_script}")
    print(f"API: PYTHONPATH={env.get('PYTHONPATH')}")
    print(f"API: PLAYWRIGHT_BROWSERS_PATH={env.get('PLAYWRIGHT_BROWSERS_PATH')}")

    # Spawn subprocess
    # On Render, we want the logs to show up in the main dashboard, so we inherit stdout/stderr
    subprocess.Popen(
        [python_exe, "-u", worker_script], 
        stdout=sys.stdout,
        stderr=sys.stderr,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
        env=env
    )
    
    return {
        "status": "accepted",
        "message": "Full scraping cycle started in background process. Refresh dashboard in 2-3 minutes."
    }
