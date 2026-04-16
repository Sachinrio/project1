import asyncio
import os
import random
import aiohttp
from typing import List, Optional

class BrowserSearcher:
    """
    Handles image searching using DuckDuckGo's internal image API.
    Uses aiohttp (lightweight HTTP) instead of Playwright — no browser needed.
    This is critical on Render's free tier where spawning extra browsers causes OOM.
    """
    
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]

    async def _get_ddg_vqd(self, session: aiohttp.ClientSession, query: str) -> Optional[str]:
        """Gets the VQD token needed for DuckDuckGo image search API."""
        try:
            headers = {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html",
            }
            url = f"https://duckduckgo.com/?q={query}&ia=images"
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return None
                text = await resp.text()
                # Extract vqd token from embedded JS
                vqd_start = text.find("vqd='")
                if vqd_start == -1:
                    vqd_start = text.find('vqd="')
                    if vqd_start == -1:
                        # Try the other format
                        import re
                        match = re.search(r'vqd=([\d-]+)', text)
                        if match:
                            return match.group(1)
                        return None
                    vqd_start += 5
                    vqd_end = text.find('"', vqd_start)
                else:
                    vqd_start += 5
                    vqd_end = text.find("'", vqd_start)
                return text[vqd_start:vqd_end]
        except Exception as e:
            print(f"BrowserSearcher: VQD fetch failed: {e}")
            return None

    async def search_images(self, query: str, max_results: int = 8) -> List[str]:
        """
        Searches DuckDuckGo Images API (no Playwright/browser needed).
        Falls back to Unsplash topic images if DDG fails.
        """
        print(f"BrowserSearcher: HTTP image search for '{query}'...")
        image_urls = []
        
        try:
            headers = {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Referer": "https://duckduckgo.com/",
                "X-Requested-With": "XMLHttpRequest",
            }
            
            connector = aiohttp.TCPConnector(limit=5, ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                # Step 1: Get VQD token
                vqd = await self._get_ddg_vqd(session, query)
                if not vqd:
                    print("BrowserSearcher: Failed to get VQD token.")
                    return self._unsplash_fallback(query)
                
                print(f"BrowserSearcher: Got VQD token. Querying images API...")
                
                # Step 2: Query the image results API
                params = {
                    "l": "wt-wt",
                    "o": "json",
                    "q": query,
                    "vqd": vqd,
                    "f": ",,,,,",
                    "p": "1",
                }
                img_api_url = "https://duckduckgo.com/i.js"
                
                async with session.get(
                    img_api_url, 
                    params=params, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=12)
                ) as resp:
                    if resp.status != 200:
                        print(f"BrowserSearcher: Image API returned {resp.status}")
                        return self._unsplash_fallback(query)
                    
                    data = await resp.json(content_type=None)
                    results = data.get("results", [])
                    print(f"BrowserSearcher: Got {len(results)} results from DDG API.")
                    
                    for r in results[:max_results]:
                        url = r.get("image") or r.get("thumbnail")
                        if url and url.startswith("http"):
                            # Skip known bad domains
                            skip = ["shutterstock.com", "gettyimages.com", "istockphoto.com", "alamy.com"]
                            if not any(s in url for s in skip):
                                image_urls.append(url)
        
        except asyncio.TimeoutError:
            print("BrowserSearcher: Timeout on HTTP image search.")
        except Exception as e:
            print(f"BrowserSearcher Error: {e}")
        
        if not image_urls:
            print("BrowserSearcher: No images found, using Unsplash fallback.")
            return self._unsplash_fallback(query)
        
        print(f"BrowserSearcher: Returning {len(image_urls)} images.")
        return image_urls

    def _unsplash_fallback(self, query: str) -> List[str]:
        """Returns a curated set of Unsplash images relevant to business/events."""
        pools = {
            "business": [
                "https://images.unsplash.com/photo-1540575861501-7cf05a4b125a?q=80&w=1000&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1505373630103-89d00c2a5851?q=80&w=1000&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?q=80&w=1000&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?q=80&w=1000&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1582192730841-2a682d7375f9?q=80&w=1000&auto=format&fit=crop",
            ],
            "tech": [
                "https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=1000&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?q=80&w=1000&auto=format&fit=crop",
            ],
            "workshop": [
                "https://images.unsplash.com/photo-1531482615713-2afd69097998?q=80&w=1000&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1540575861501-7cf05a4b125a?q=80&w=1000&auto=format&fit=crop",
            ],
            "networking": [
                "https://images.unsplash.com/photo-1528605105345-5344ea20e269?q=80&w=1000&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?q=80&w=1000&auto=format&fit=crop",
            ],
        }
        q = query.lower()
        for key, images in pools.items():
            if key in q:
                return images
        return pools["business"]

# Singleton instance
browser_searcher = BrowserSearcher()
