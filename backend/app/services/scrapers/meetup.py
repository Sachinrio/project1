"""
Meetup Scraper — HTTP-only (no Playwright/Chromium).
Uses the Meetup public GraphQL API to fetch Chennai business events.
This is reliable and uses ~5MB RAM instead of ~400MB for Chromium.
"""

import aiohttp
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict
from .utils import is_business_event

IMAGE_POOL = [
    "https://images.unsplash.com/photo-1540575861501-7cf05a4b125a?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1505373630103-89d00c2a5851?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1528605105345-5344ea20e269?q=80&w=1000&auto=format&fit=crop",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.meetup.com/",
}

MEETUP_GQL_URL = "https://www.meetup.com/gql2"

GQL_QUERY = """
query CategorySearch($input: ConnectionInput!, $filter: SearchConnectionFilter!) {
  rankedEvents(input: $input, filter: $filter) {
    edges {
      node {
        id
        title
        eventUrl
        dateTime
        endTime
        description
        venue { name address city }
        imageUrl
        group { name }
      }
    }
  }
}
"""

class MeetupScraper:
    async def scrape_http(self) -> List[Dict]:
        print("MeetupScraper (HTTP): Starting...")
        events = []

        payload = {
            "operationName": "CategorySearch",
            "query": GQL_QUERY,
            "variables": {
                "input": {"first": 30},
                "filter": {
                    "query": "business",
                    "lat": 13.0827,
                    "lon": 80.2707,
                    "radius": 50,
                    "source": "EVENTS",
                }
            }
        }

        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:
                async with session.post(MEETUP_GQL_URL, json=payload) as resp:
                    if resp.status != 200:
                        print(f"MeetupScraper: GQL returned {resp.status}. Trying RSS fallback...")
                        return await self._rss_fallback(session)
                    
                    data = await resp.json()
                    edges = data.get("data", {}).get("rankedEvents", {}).get("edges", [])
                    print(f"MeetupScraper: GQL returned {len(edges)} events.")
                    
                    if not edges:
                        return await self._rss_fallback(session)

                    for edge in edges:
                        try:
                            node = edge.get("node", {})
                            title = node.get("title", "Untitled Meetup")
                            url = node.get("eventUrl", "")
                            dt_str = node.get("dateTime", "")
                            end_str = node.get("endTime", "")
                            description = node.get("description", "") or f"Join this Meetup event: {title}"
                            image = node.get("imageUrl") or IMAGE_POOL[abs(hash(title)) % len(IMAGE_POOL)]
                            venue_obj = node.get("venue") or {}
                            venue = venue_obj.get("name") or "Chennai"

                            start_time = datetime.now() + timedelta(days=7)
                            end_time = start_time + timedelta(hours=2)
                            if dt_str:
                                try:
                                    start_time = datetime.fromisoformat(dt_str.replace("Z", "+00:00")).replace(tzinfo=None)
                                    end_time = start_time + timedelta(hours=2)
                                except Exception:
                                    pass
                            if end_str:
                                try:
                                    end_time = datetime.fromisoformat(end_str.replace("Z", "+00:00")).replace(tzinfo=None)
                                except Exception:
                                    pass

                            event_data = {
                                "eventbrite_id": f"meetup_{hashlib.md5(url.encode()).hexdigest()[:12]}",
                                "title": title[:100],
                                "description": description[:500],
                                "start_time": start_time,
                                "end_time": end_time,
                                "url": url,
                                "image_url": image,
                                "venue_name": venue,
                                "venue_address": "Chennai, India",
                                "organizer_name": node.get("group", {}).get("name", "Meetup Group"),
                                "is_free": False,
                                "online_event": False,
                                "category": "Business",
                                "raw_data": {"source": "meetup_gql"}
                            }

                            if is_business_event(event_data):
                                events.append(event_data)
                            else:
                                print(f"  [Filtered] Non-business: {title}")
                        except Exception as e:
                            print(f"MeetupScraper: Error parsing edge: {e}")
                            continue

        except asyncio.TimeoutError:
            print("MeetupScraper: Request timed out.")
        except Exception as e:
            print(f"MeetupScraper: HTTP error: {e}")

        print(f"MeetupScraper: Collected {len(events)} events.")
        return events

    async def _rss_fallback(self, session: aiohttp.ClientSession) -> List[Dict]:
        """Fallback: Fetch Meetup Chennai RSS feed for events."""
        print("MeetupScraper: Trying RSS fallback...")
        events = []
        rss_urls = [
            "https://www.meetup.com/find/events/rss/?location=in--Chennai&category=career-business",
        ]
        try:
            from bs4 import BeautifulSoup
            import dateparser

            for rss_url in rss_urls:
                try:
                    async with session.get(rss_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                        if resp.status != 200:
                            continue
                        xml = await resp.text()
                        soup = BeautifulSoup(xml, "lxml-xml")
                        items = soup.find_all("item")
                        print(f"MeetupScraper RSS: Found {len(items)} items.")
                        for item in items[:20]:
                            try:
                                title = item.find("title").text.strip() if item.find("title") else "Meetup Event"
                                link = item.find("link").text.strip() if item.find("link") else ""
                                pub_date = item.find("pubDate")
                                start_time = datetime.now() + timedelta(days=7)
                                if pub_date:
                                    parsed = dateparser.parse(pub_date.text)
                                    if parsed:
                                        start_time = parsed.replace(tzinfo=None)

                                event_data = {
                                    "eventbrite_id": f"meetup_{hashlib.md5(link.encode()).hexdigest()[:12]}",
                                    "title": title[:100],
                                    "description": f"Join this Meetup event: {title}",
                                    "start_time": start_time,
                                    "end_time": start_time + timedelta(hours=2),
                                    "url": link,
                                    "image_url": IMAGE_POOL[abs(hash(title)) % len(IMAGE_POOL)],
                                    "venue_name": "Chennai",
                                    "venue_address": "Chennai, India",
                                    "organizer_name": "Meetup Group",
                                    "is_free": False,
                                    "online_event": False,
                                    "category": "Business",
                                    "raw_data": {"source": "meetup_rss"}
                                }
                                if is_business_event(event_data):
                                    events.append(event_data)
                            except Exception as e:
                                print(f"MeetupScraper RSS item error: {e}")
                                continue
                except Exception as e:
                    print(f"MeetupScraper RSS fetch error for {rss_url}: {e}")
        except Exception as e:
            print(f"MeetupScraper RSS fallback error: {e}")
        return events

    # Keep a stub for compatibility with any code expecting `scrape(page)`
    async def scrape(self, page=None) -> List[Dict]:
        return await self.scrape_http()
