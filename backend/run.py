import sys
import asyncio
import uvicorn

if __name__ == "__main__":
    # Force Proactor Loop for Playwright on Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        print("Windows Proactor Loop Policy Applied.")

    print("Starting Server with Custom Runner (NO RELOAD - REQUIRED FOR PLAYWRIGHT ON WINDOWS)...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, reload=False)
