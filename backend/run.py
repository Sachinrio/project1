import sys
import asyncio
import uvicorn

import os

if __name__ == "__main__":
    import os
    
    # 1. Setup Custom Playwright Path for Render Cloud Deployment
    # We installed chromium locally to ./pw-browsers during build.sh
    root_dir = os.path.dirname(os.path.abspath(__file__))
    custom_pw_path = os.path.join(root_dir, "pw-browsers")
    
    # Check if the path is already set by render_start.sh (preferred)
    env_pw_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    
    if env_pw_path and os.path.exists(env_pw_path):
        print(f"STARTUP: Using PLAYWRIGHT_BROWSERS_PATH from environment: {env_pw_path}")
    elif os.path.exists(custom_pw_path):
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = custom_pw_path
        print(f"STARTUP: Found custom browsers at {custom_pw_path}")
    else:
        print(f"WARNING: Playwright browsers NOT FOUND at {custom_pw_path} or via ENV.")
        print("Scrapers will likely fail unless 'playwright install' was run globally.")

    # 2. Force Proactor Loop for Playwright on Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        print("Windows Proactor Loop Policy Applied.")

    port = int(os.getenv("PORT", 8001))
    print(f"Starting Server with Custom Runner (NO RELOAD - REQUIRED FOR PLAYWRIGHT ON WINDOWS)... Listening on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
