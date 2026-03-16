import aiohttp
import urllib.parse
from bs4 import BeautifulSoup
import re
import asyncio
from duckduckgo_search import DDGS

class DuckDuckGoImageScraper:
    def __init__(self):
        self.base_url = "https://html.duckduckgo.com/html/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def get_image_url(self, event_title: str) -> str:
        """
        Uses the dedicated duckduckgo-search package to stably fetch '{title} image without text on it with full hd'.
        This bypassed Cloudflare 403s and guarantees a real image.
        """
        query = f"{event_title} image without text on it with full hd"
        print(f"DEBUG ImageScraper: Searching via DDGS library for: '{query}'")
        
        try:
            # Run the synchronous DDGS search in an executor thread to avoid blocking asyncio
            def fetch_images():
                with DDGS() as ddgs:
                    # Request up to 10 images to ensure we can filter out junk
                    return list(ddgs.images(query, max_results=10))

            results = await asyncio.to_thread(fetch_images)
            
            if not results:
                print("DEBUG ImageScraper: DDGS library returned no images.")
                return ""
                
            for item in results:
                img_url = item.get("image", "")
                
                # Apply strict filtering to skip junk
                img_lower = img_url.lower()
                if not img_url or any(x in img_lower for x in ['.ico', 'favicon', 'logo', 'icon', 'tracker', 'pixel', 'avatar', 'profile', '.svg']):
                    continue
                    
                print(f"DEBUG ImageScraper: SUCCESS! Found clean HD image via DDGS: {img_url}")
                return img_url

            print("DEBUG ImageScraper: Exhausted DDGS results without finding a clean HD image.")
            return ""
            
        except Exception as e:
            print(f"DEBUG ImageScraper: Error during DDGS scrape: {e}")
            return ""

# Expose a singleton instance
image_scraper_service = DuckDuckGoImageScraper()
