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
    if os.path.exists(custom_pw_path):
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = custom_pw_path
        print(f"Set PLAYWRIGHT_BROWSERS_PATH to {custom_pw_path}")
    else:
        print("WARNING: Custom Playwright path not found. Proceeding with system defaults.")

    # 2. Force Proactor Loop for Playwright on Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        print("Windows Proactor Loop Policy Applied.")

    port = int(os.getenv("PORT", 8001))
    print(f"Starting Server with Custom Runner (NO RELOAD - REQUIRED FOR PLAYWRIGHT ON WINDOWS)... Listening on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
