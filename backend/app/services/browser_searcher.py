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
                
                # Navigate directly to DuckDuckGo Image Search
                url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&iax=images&ia=images"
                print(f"BrowserSearcher: Navigating to {url}")
                
                # Wait for navigation and check if blocked
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                
                title = await page.title()
                if "Just a moment" in title or "Access Denied" in title:
                    print("BrowserSearcher: BLOCKED by bot detection.")
                    await browser.close()
                    return []

                # Wait for any image tile
                print("BrowserSearcher: Waiting for image tiles...")
                try:
                    await page.wait_for_selector(".tile--img, .tile--img__img", timeout=15000)
                except:
                    print("BrowserSearcher: Timeout waiting for image tiles. DOM might be different.")
                    # Take a screenshot if possible for debugging (not possible here but logging content)
                    html = await page.content()
                    print(f"BrowserSearcher: DOM Snippet: {html[:500]}")
                
                # Advanced extraction script
                print("BrowserSearcher: Extracting image URLs...")
                image_urls = await page.evaluate("""
                    () => {
                        const results = [];
                        // Strategy 1: data-zci-link
                        const tiles = document.querySelectorAll('.tile--img');
                        tiles.forEach(tile => {
                            try {
                                const data = JSON.parse(tile.getAttribute('data-zci-link') || '{}');
                                if (data.image && data.image.startsWith('http')) results.push(data.image);
                            } catch (e) {}
                        });

                        // Strategy 2: tile--img__img src
                        if (results.length < 5) {
                            const imgs = document.querySelectorAll('img.tile--img__img');
                            imgs.forEach(img => {
                                if (img.src && !img.src.includes('base64') && img.src.startsWith('http')) {
                                    results.push(img.src);
                                }
                            });
                        }
                        
                        // Strategy 3: Generic img in tile link
                        if (results.length < 5) {
                            const links = document.querySelectorAll('a[href*="img_url"]');
                            links.forEach(link => {
                                const match = link.href.match(/img_url=([^&]+)/);
                                if (match) results.push(decodeURIComponent(match[1]));
                            });
                        }

                        return [...new Set(results)]; // De-duplicate
                    }
                """)
                
                print(f"BrowserSearcher: Found {len(image_urls)} candidate images.")
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
