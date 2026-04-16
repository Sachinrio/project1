"""
Chennai Trade Centre (CTC) Scraper — HTTP-only (no Playwright/Chromium).
CTC is an ASP.NET site. We fetch HTML and parse .schedule-item blocks with BeautifulSoup.
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
    "https://images.unsplash.com/photo-1582192730841-2a682d7375f9?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1540575861501-7cf05a4b125a?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1505373630103-89d00c2a5851?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1431540015161-0bf868a2d407?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1560179707-f14e90ef3623?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?q=80&w=1000&auto=format&fit=crop"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

TARGET_URL = "https://www.chennaitradecentre.in/UpcomingEvents.aspx?etype=1"

class CTCScraper:
    async def scrape_http(self) -> List[Dict]:
        print("CTCScraper (HTTP): Starting...")
        events = []

        try:
            timeout = aiohttp.ClientTimeout(total=25)
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout, connector=connector) as session:
                async with session.get(TARGET_URL) as resp:
                    if resp.status != 200:
                        print(f"CTCScraper: Got status {resp.status}. Skipping.")
                        return []

                    html = await resp.text()
                    print(f"CTCScraper: Got HTML ({len(html)} chars). Parsing...")
                    soup = BeautifulSoup(html, "lxml")

                    # CTC uses .schedule-item for each event row
                    items = soup.select(".schedule-item")
                    
                    # Fallbacks for different page structures
                    if not items:
                        items = soup.select(".event-item") or soup.select("tr.event-row") or soup.select("[class*='schedule']")
                    
                    # Broader fallback: look for any table rows with date-like text
                    if not items:
                        items = soup.select("table tr")[1:]  # Skip header row

                    print(f"CTCScraper: Found {len(items)} items.")

                    now = datetime.now()
                    six_months_later = now + timedelta(days=180)

                    for item in items:
                        try:
                            # Title: usually in h4
                            title_el = item.select_one("h4") or item.select_one("h3") or item.select_one(".title")
                            title = title_el.get_text(strip=True) if title_el else ""
                            
                            # Try td cells for table-structured pages
                            if not title:
                                cells = item.find_all("td")
                                if cells:
                                    title = cells[0].get_text(strip=True)
                            
                            if not title:
                                continue

                            # Date: look for calendar icon li or any li with a date-like text
                            date_text = ""
                            date_li = item.select_one("li:has(i.fa-calendar)") or \
                                      item.select_one(".schedule-meta li")
                            if date_li:
                                date_text = date_li.get_text(strip=True)
                            else:
                                # Fallback: grab all li text and find one that looks like a date
                                for li in item.select("li"):
                                    text = li.get_text(strip=True)
                                    if any(m in text for m in ["Jan","Feb","Mar","Apr","May","Jun",
                                                                "Jul","Aug","Sep","Oct","Nov","Dec",
                                                                "2025","2026","2027"]):
                                        date_text = text
                                        break
                                # Table cell fallback
                                if not date_text:
                                    cells = item.find_all("td")
                                    for cell in cells:
                                        text = cell.get_text(strip=True)
                                        if any(m in text for m in ["Jan","Feb","Mar","Apr","May","Jun",
                                                                    "Jul","Aug","Sep","Oct","Nov","Dec"]):
                                            date_text = text
                                            break

                            start_time = None
                            if date_text:
                                first_part = date_text.split(" - ")[0].split("–")[0].strip()
                                # Remove icon text if any (like calendar icons that render as text)
                                first_part = "".join(c for c in first_part if c.isprintable()).strip()
                                start_time = dateparser.parse(
                                    first_part,
                                    settings={"DATE_ORDER": "DMY", "PREFER_DATES_FROM": "future"}
                                )

                            if not start_time:
                                continue

                            start_time = start_time.replace(tzinfo=None) if start_time.tzinfo else start_time

                            if start_time < now.replace(hour=0, minute=0, second=0, microsecond=0):
                                continue
                            if start_time > six_months_later:
                                continue

                            # Organizer
                            org_el = item.select_one("h6 + span") or item.select_one(".organizer")
                            organizer = org_el.get_text(strip=True) if org_el else "Chennai Trade Centre"

                            img_idx = abs(hash(title)) % len(IMAGE_POOL)
                            event_data = {
                                "eventbrite_id": f"ctc_{int(start_time.timestamp())}_{hashlib.md5(title.encode()).hexdigest()[:6]}",
                                "title": title,
                                "description": f"Trade Exhibition at Chennai Trade Centre organized by {organizer}.",
                                "start_time": start_time,
                                "end_time": start_time + timedelta(hours=8),
                                "url": TARGET_URL,
                                "image_url": IMAGE_POOL[img_idx],
                                "venue_name": "Chennai Trade Centre",
                                "venue_address": "CTC Complex, Nandambakkam, Chennai",
                                "organizer_name": organizer,
                                "is_free": False,
                                "online_event": False,
                                "category": "Business",
                                "raw_data": {"source": "trade_centre"}
                            }

                            if is_business_event(event_data):
                                events.append(event_data)
                            else:
                                print(f"  [Filtered] Non-business: {title}")

                        except Exception as e:
                            print(f"CTCScraper: Item parse error: {e}")
                            continue

        except asyncio.TimeoutError:
            print("CTCScraper: Request timed out.")
        except Exception as e:
            print(f"CTCScraper: HTTP error: {e}")

        print(f"CTCScraper: Collected {len(events)} events.")
        return events

    # Stub for compatibility
    async def scrape(self, page=None) -> List[Dict]:
        return await self.scrape_http()
