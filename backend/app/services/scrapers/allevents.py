"""
AllEvents Scraper — HTTP-only (no Playwright/Chromium).
Uses aiohttp + BeautifulSoup to parse allevents.in Chennai business page.
"""

import aiohttp
import asyncio
import hashlib
import dateparser
from datetime import datetime, timedelta
from typing import List, Dict
from bs4 import BeautifulSoup
from .utils import is_business_event

IMAGE_POOL = [
    "https://images.unsplash.com/photo-1540575861501-7cf05a4b125a?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1505373630103-89d00c2a5851?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1582192730841-2a682d7375f9?q=80&w=1000&auto=format&fit=crop",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

class AllEventsScraper:
    async def scrape_http(self) -> List[Dict]:
        print("AllEventsScraper (HTTP): Starting...")
        events = []
        target_url = "https://allevents.in/chennai/business"

        try:
            timeout = aiohttp.ClientTimeout(total=30)
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout, connector=connector) as session:
                async with session.get(target_url) as resp:
                    if resp.status != 200:
                        print(f"AllEventsScraper: Got status {resp.status}. Trying API endpoint...")
                        return await self._try_api(session)

                    html = await resp.text()
                    print(f"AllEventsScraper: Got HTML ({len(html)} chars). Parsing...")
                    
                    soup = BeautifulSoup(html, "lxml")
                    
                    # Try multiple card selectors AllEvents uses
                    cards = soup.select(".event-card") or \
                            soup.select("li[data-link]") or \
                            soup.select("div.event-item") or \
                            soup.select("[class*='event-card']")
                    
                    print(f"AllEventsScraper: Found {len(cards)} cards in HTML.")
                    
                    if not cards:
                        # Try JSON-LD embedded data (AllEvents sometimes embeds it)
                        events = self._parse_json_ld(soup)
                        if events:
                            print(f"AllEventsScraper: Got {len(events)} events from JSON-LD.")
                            return events
                        print("AllEventsScraper: No cards found, trying API...")
                        return await self._try_api(session)

                    for card in cards[:30]:
                        try:
                            title_el = card.select_one(".title") or card.select_one("h3") or card.select_one("h2")
                            title = title_el.get_text(strip=True) if title_el else "Unknown Event"
                            if not title or title == "Unknown Event":
                                continue

                            link_el = card.select_one("a")
                            link = link_el.get("href", "") if link_el else ""
                            if link and not link.startswith("http"):
                                link = "https://allevents.in" + link

                            time_el = card.select_one(".time") or card.select_one(".date") or card.select_one("[class*='date']")
                            time_str = time_el.get_text(strip=True) if time_el else ""

                            venue_el = card.select_one(".subtitle") or card.select_one(".location") or card.select_one("[class*='venue']")
                            venue = venue_el.get_text(strip=True) if venue_el else "Chennai"

                            # Image extraction
                            img_el = card.select_one("img[data-src]") or \
                                     card.select_one("img[src*='banner']") or \
                                     card.select_one("img")
                            event_image = None
                            if img_el:
                                for attr in ["data-src", "data-img", "data-lazy-src", "srcset", "src"]:
                                    val = img_el.get(attr, "")
                                    if val:
                                        candidate = val.split(",")[0].split(" ")[0].strip()
                                        if candidate.startswith("//"):
                                            candidate = "https:" + candidate
                                        skip = ["og-logo", "logo.jpg", "logo.png", "placeholder", "blank.gif", "data:image"]
                                        if candidate.startswith("http") and not any(s in candidate.lower() for s in skip):
                                            event_image = candidate
                                            break

                            if not event_image:
                                event_image = IMAGE_POOL[abs(hash(title)) % len(IMAGE_POOL)]

                            start_time = datetime.now() + timedelta(days=2)
                            if time_str:
                                parsed = dateparser.parse(time_str.replace('\n', ' ').strip())
                                if parsed:
                                    start_time = parsed.replace(tzinfo=None) if parsed.tzinfo else parsed

                            event_id = hashlib.md5(link.split("?")[0].encode()).hexdigest()
                            event_data = {
                                "title": title,
                                "description": f"Business event in Chennai: {title}",
                                "start_time": start_time,
                                "end_time": start_time + timedelta(hours=3),
                                "url": link,
                                "venue_name": venue[:100],
                                "image_url": event_image,
                                "eventbrite_id": f"allevents-{event_id}",
                                "is_free": False,
                                "category": "Business",
                                "raw_data": {"source": "allevents"}
                            }

                            if is_business_event(event_data):
                                events.append(event_data)
                            else:
                                print(f"  [Filtered] Non-business: {title}")

                        except Exception as e:
                            print(f"AllEventsScraper: Card parse error: {e}")
                            continue

        except asyncio.TimeoutError:
            print("AllEventsScraper: Request timed out.")
        except Exception as e:
            print(f"AllEventsScraper: HTTP error: {e}")

        print(f"AllEventsScraper: Collected {len(events)} events.")
        return events

    async def _try_api(self, session: aiohttp.ClientSession) -> List[Dict]:
        """Try AllEvents internal API (JSON endpoint)."""
        events = []
        try:
            api_url = "https://allevents.in/api/index.php"
            params = {
                "type": "city-category",
                "city": "chennai",
                "category": "business",
                "limit": "30",
            }
            async with session.get(api_url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    items = data if isinstance(data, list) else data.get("events", [])
                    print(f"AllEventsScraper API: Got {len(items)} items.")
                    for item in items[:20]:
                        try:
                            title = item.get("title") or item.get("name") or "AllEvents Event"
                            link = item.get("event_url") or item.get("url") or ""
                            start_ts = item.get("start_time") or item.get("starttime")
                            start_time = datetime.fromtimestamp(int(start_ts)) if start_ts else datetime.now() + timedelta(days=2)
                            image = item.get("pic") or item.get("thumbnail") or IMAGE_POOL[abs(hash(title)) % len(IMAGE_POOL)]
                            events.append({
                                "title": title,
                                "description": f"Business event: {title}",
                                "start_time": start_time,
                                "end_time": start_time + timedelta(hours=3),
                                "url": link,
                                "venue_name": item.get("venue", {}).get("name", "Chennai") if isinstance(item.get("venue"), dict) else "Chennai",
                                "image_url": image,
                                "eventbrite_id": f"allevents-{hashlib.md5(link.encode()).hexdigest()[:12]}",
                                "is_free": False,
                                "category": "Business",
                                "raw_data": {"source": "allevents_api"}
                            })
                        except Exception as e:
                            print(f"AllEventsScraper API item error: {e}")
        except Exception as e:
            print(f"AllEventsScraper API error: {e}")
        return events

    def _parse_json_ld(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract events from JSON-LD structured data embedded in the page."""
        import json, re
        events = []
        try:
            scripts = soup.find_all("script", type="application/ld+json")
            for script in scripts:
                try:
                    data = json.loads(script.string or "")
                    if isinstance(data, list):
                        items = data
                    elif data.get("@type") == "ItemList":
                        items = [i.get("item", {}) for i in data.get("itemListElement", [])]
                    elif data.get("@type") == "Event":
                        items = [data]
                    else:
                        continue
                    for item in items[:20]:
                        if item.get("@type") != "Event":
                            continue
                        title = item.get("name", "Event")
                        url = item.get("url", "")
                        start_str = item.get("startDate", "")
                        start_time = datetime.now() + timedelta(days=2)
                        if start_str:
                            parsed = dateparser.parse(start_str)
                            if parsed:
                                start_time = parsed.replace(tzinfo=None) if parsed.tzinfo else parsed
                        loc = item.get("location", {})
                        venue = loc.get("name", "Chennai") if isinstance(loc, dict) else "Chennai"
                        image = ""
                        img_data = item.get("image")
                        if isinstance(img_data, str):
                            image = img_data
                        elif isinstance(img_data, dict):
                            image = img_data.get("url", "")
                        if not image:
                            image = IMAGE_POOL[abs(hash(title)) % len(IMAGE_POOL)]
                        events.append({
                            "title": title,
                            "description": item.get("description", f"Business event: {title}")[:500],
                            "start_time": start_time,
                            "end_time": start_time + timedelta(hours=3),
                            "url": url,
                            "venue_name": venue,
                            "image_url": image,
                            "eventbrite_id": f"allevents-{hashlib.md5(url.encode()).hexdigest()[:12]}",
                            "is_free": False,
                            "category": "Business",
                            "raw_data": {"source": "allevents_jsonld"}
                        })
                except Exception:
                    continue
        except Exception as e:
            print(f"AllEventsScraper JSON-LD error: {e}")
        return events

    # Stub for compatibility
    async def scrape(self, page=None) -> List[Dict]:
        return await self.scrape_http()
