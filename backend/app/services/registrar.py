import asyncio
from playwright.async_api import async_playwright
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def auto_register_playwright(event_url: str, user_first_name: str, user_last_name: str, user_email: str):
    """
    Co-pilot Mode: Opens a visible browser, navigates to checkout, 
    and waits for the user to complete the process manually.
    """
    logger.info(f"Registrar: Starting Co-pilot for {event_url}")
    
    async with async_playwright() as p:
        # 1. LAUNCH VISIBLE BROWSER
        browser = await p.chromium.launch(
            headless=False, # VISIBLE
            args=[
                '--disable-blink-features=AutomationControlled',
                '--start-maximized' 
            ]
        )
        
        # Configure context
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        
        page = await context.new_page()
        
        try:
            # 2. Navigate
            logger.info("Navigating to event page...")
            await page.goto(event_url, timeout=60000)
            
            # 3. Attempt to click "Get Tickets" or "Register"
            # This helps the user skip the first step.
            get_tickets_btn = page.locator("button:has-text('Reserve a spot'), a:has-text('Reserve a spot'), button:has-text('Register'), a:has-text('Register'), button:has-text('Get tickets'), a:has-text('Get tickets')").first
            
            try:
                if await get_tickets_btn.is_visible(timeout=5000):
                    logger.info("Auto-clicking 'Get Tickets'...")
                    await get_tickets_btn.click()
                else:
                    logger.info("'Get Tickets' button not immediately visible, user might need to scroll or select it.")
            except Exception:
                pass # It's okay, user is there to handle it.

            # 4. PERSISTENCE LOOP (Keep Alive)
            logger.info("✅ Browser is open. Waiting for user to close it...")
            
            # We assume the user will close the browser window when done.
            # We poll is_connected() to keep the loop running.
            while browser.is_connected():
                await asyncio.sleep(1)
                
            logger.info("User closed the browser. Session ended.")

        except Exception as e:
            logger.error(f"Registrar Error: {e}")
        finally:
            # Cleanup if not already closed
            if browser.is_connected():
                await browser.close()
