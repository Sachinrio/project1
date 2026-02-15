import asyncio
import os
import random
from typing import List, Optional
from playwright.async_api import async_playwright

class BrowserSearcher:
    """
    Handles browser-based image searching using Playwright.
    Bypasses API blocks by mimicking a real user on DuckDuckGo.
    """
    
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]

    async def search_images(self, query: str, max_results: int = 8) -> List[str]:
        """
        Navigates to DuckDuckGo Images and scrapes candidate URLs.
        """
        print(f"BrowserSearcher: Starting search for '{query}'...")
        image_urls = []
        
        async with async_playwright() as p:
            # Check for local playwright browsers path (Render config)
            browser_path = os.getenv("PLAYWRIGHT_BROWSERS_PATH")
            print(f"DEBUG: BrowserSearcher - PLAYWRIGHT_BROWSERS_PATH={browser_path}")
            if browser_path and os.path.exists(browser_path):
                print(f"DEBUG: BrowserSearcher - Path exists: {browser_path}")
            elif browser_path:
                print(f"DEBUG: BrowserSearcher - WARNING: Path DOES NOT exist: {browser_path}")
            
            try:
                print(f"DEBUG: BrowserSearcher - Launching Chromium (Headless)...")
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox", 
                        "--disable-setuid-sandbox", 
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--no-first-run",
                        "--no-zygote"
                    ]
                )
                print(f"DEBUG: BrowserSearcher - Browser launched successfully.")
                
                context = await browser.new_context(
                    user_agent=random.choice(self.user_agents),
                    viewport={'width': 1280, 'height': 720}
                )
                
                page = await context.new_page()
                
                # Use Stealth pattern from scraper.py
                from playwright_stealth import Stealth
                await Stealth().apply_stealth_async(page)
                
                # 1. Navigate to DuckDuckGo Homepage
                print("BrowserSearcher: Navigating to https://duckduckgo.com/")
                # Use domcontentloaded for speed (networkidle is too slow on Render)
                await page.goto("https://duckduckgo.com/", wait_until="domcontentloaded", timeout=20000)
                
                # 2. Type search query into the search field
                search_query = query
                print(f"BrowserSearcher: Typing query: '{search_query}'")
                
                try:
                    # Faster selector wait
                    search_input = await page.wait_for_selector('input[name="q"]', timeout=7000)
                    await search_input.fill(search_query)
                    await search_input.press("Enter")
                    
                    # 3. Wait for results and switch to Images tab
                    print("BrowserSearcher: Waiting for results...")
                    await page.wait_for_load_state("domcontentloaded")
                    
                    images_tab = await page.wait_for_selector('a[data-zci-link="images"]', timeout=7000)
                    await images_tab.click()
                    print("BrowserSearcher: Switched to Images tab.")
                except Exception as e:
                    print(f"BrowserSearcher: Homepage interaction slow or failed ({e}). Forcing direct image URL.")
                    url = f"https://duckduckgo.com/?q={search_query.replace(' ', '+')}&iax=images&ia=images"
                    await page.goto(url, wait_until="domcontentloaded", timeout=15000)

                title = await page.title()
                if "Just a moment" in title or "Access Denied" in title:
                    print("BrowserSearcher: BLOCKED by bot detection.")
                    await browser.close()
                    return []

                # Wait for any image tile (Faster timeout)
                print("BrowserSearcher: Waiting for image tiles...")
                try:
                    await page.wait_for_selector(".tile--img, .tile--img__img", timeout=10000)
                except:
                    print("BrowserSearcher: Timeout waiting for image tiles.")
                    # Take a screenshot if possible for debugging (not possible here but logging content)
                    html = await page.content()
                    print(f"BrowserSearcher: DOM Snippet: {html[:500]}")
                
                # Advanced extraction script
                print("BrowserSearcher: Extracting image URLs...")
                image_data = await page.evaluate("""
                    () => {
                        const results = [];
                        
                        // Strategy 1: data-zci-link (The most reliable DDG structure)
                        const tiles = document.querySelectorAll('.tile--img');
                        tiles.forEach(tile => {
                            try {
                                const data = JSON.parse(tile.getAttribute('data-zci-link') || '{}');
                                if (data.image && data.image.startsWith('http')) results.push(data.image);
                            } catch (e) {}
                        });

                        // Strategy 2: tile--img__img src (Backup)
                        const imgs = document.querySelectorAll('img.tile--img__img');
                        imgs.forEach(img => {
                            if (img.src && !img.src.includes('base64') && img.src.startsWith('http')) {
                                results.push(img.src);
                            } else if (img.dataset.src && img.dataset.src.startsWith('http')) {
                                results.push(img.dataset.src);
                            }
                        });
                        
                        // Strategy 3: DuckDuckGo proxy URLs (Last resort)
                        const proxies = document.querySelectorAll('img[src*="external-content.duckduckgo.com"]');
                        proxies.forEach(img => {
                            if (img.src.startsWith('http')) results.push(img.src);
                        });

                        return [...new Set(results)]; // De-duplicate
                    }
                """)
                
                image_urls = image_data
                print(f"BrowserSearcher: Found {len(image_urls)} candidate images.")
                
                if not image_urls:
                    print("BrowserSearcher: DEBUG - No images found. Sniffing DOM...")
                    html = await page.content()
                    print(f"BrowserSearcher: DOM Snippet: {html[:1000]}")
                
                await browser.close()
                
            except Exception as e:
                print(f"BrowserSearcher Error: {e}")
                if 'browser' in locals():
                    try:
                        await browser.close()
                    except:
                        pass
                    
        return image_urls[:max_results]

# Singleton instance
browser_searcher = BrowserSearcher()
