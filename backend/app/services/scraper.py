"""
Eventbrite Scraper — HTTP-only (no Playwright/Chromium).
Strategy:
  1. Hit the Eventbrite Search API directly (private but stable JSON API).
  2. For each found event ID, call the official Eventbrite public API for full details.
  3. Falls back to scraping the HTML search page with aiohttp if the search API is blocked.
"""

import asyncio
import aiohttp
import requests
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from app.services.scrapers.utils import is_business_event

# --- CONSTANTS ---
BASE_URL = "https://www.eventbrite.com"
EVENTBRITE_API_TOKEN = "T6WRADHDNPM5S4VYLFR5"

IMAGE_POOL = [
    "https://images.unsplash.com/photo-1540575861501-7cf05a4b125a?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1505373630103-89d00c2a5851?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?q=80&w=1000&auto=format&fit=crop",
]

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.eventbrite.com/",
    "DNT": "1",
}


def fetch_event_details_api(event_id: str, fallback_image: str = None) -> Optional[Dict]:
    """
    Fetches event details from the official Eventbrite API.
    Returns a cleaned dict or None if the call fails.
    """
    url = f"https://www.eventbriteapi.com/v3/events/{event_id}/"
    headers = {"Authorization": f"Bearer {EVENTBRITE_API_TOKEN}"}
    params = {"expand": "venue,ticket_classes,organizer"}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()

            start_str = data.get("start", {}).get("local")
            end_str = data.get("end", {}).get("local")
            start_time = datetime.fromisoformat(start_str) if start_str else datetime.now()
            end_time = datetime.fromisoformat(end_str) if end_str else start_time + timedelta(hours=2)

            # Recurring event fix
            now = datetime.now(start_time.tzinfo)
            if start_time < now and end_time > now:
                duration = end_time - start_time
                if duration.days > 7:
                    days_since_start = (now - start_time).days
                    weeks_passed = (days_since_start // 7) + 1
                    next_start = start_time + timedelta(weeks=weeks_passed)
                    if next_start < end_time:
                        print(f"  [Recurrence Fix] Moving to {next_start.date()}")
                        start_time = next_start

            is_free = data.get("is_free", False)
            online_event = data.get("online_event", False)

            venue = data.get("venue")
            if venue:
                venue_name = venue.get("name") or "TBD"
                address_obj = venue.get("address") or {}
                venue_address = (
                    address_obj.get("localized_address_display")
                    or address_obj.get("address_1")
                    or address_obj.get("city")
                    or "Chennai, India"
                )
            else:
                venue_name = "Online Event"
                venue_address = "Online"
                online_event = True

            organizer = data.get("organizer") or {}
            organizer_name = organizer.get("name") or "Unknown Organizer"

            name_obj = data.get("name") or {}
            desc_obj = data.get("description") or {}
            logo_obj = data.get("logo") or {}
            logo_url = logo_obj.get("url")

            if not logo_url or "placeholder" in (logo_url or "").lower():
                logo_url = fallback_image
            if not logo_url or "placeholder" in (logo_url or "").lower():
                logo_url = IMAGE_POOL[abs(hash(name_obj.get("text", ""))) % len(IMAGE_POOL)]

            return {
                "title": name_obj.get("text", "Untitled Event"),
                "description": desc_obj.get("text", ""),
                "start_time": start_time,
                "end_time": end_time,
                "is_free": is_free,
                "online_event": online_event,
                "venue_name": venue_name,
                "venue_address": venue_address,
                "organizer_name": organizer_name,
                "url": data.get("url"),
                "logo_url": logo_url,
            }
        else:
            print(f"API Error for {event_id}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception fetching API for {event_id}: {e}")
        return None


async def _search_via_api(city: str = "chennai", category: str = "business") -> List[str]:
    """
    Calls Eventbrite's internal search API (JSON) to get event IDs.
    Returns a list of event IDs.
    """
    event_ids = []
    try:
        # Eventbrite's internal search endpoint (stable, returns JSON)
        search_url = f"{BASE_URL}/api/v3/destination/search/"
        params = {
            "expand.destination_event": "primary_venue,image,tags,saves,primary_organizer,ticket_availability",
            "page_size": 20,
            "q": f"{category} events in {city}",
            "places": "Chennai",
            "online_events_only": "false",
            "client_timezone": "Asia/Kolkata",
            "aff": "ebdssbdestsearch",
        }
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(headers=BROWSER_HEADERS, timeout=timeout) as session:
            async with session.get(search_url, params=params) as resp:
                if resp.status != 200:
                    print(f"Eventbrite internal API: status {resp.status}")
                    return []
                data = await resp.json(content_type=None)
                events_section = data.get("events", {})
                results = events_section.get("results", [])
                print(f"Eventbrite internal API: {len(results)} results.")
                for r in results:
                    eid = str(r.get("id") or "")
                    if eid:
                        event_ids.append(eid)
    except Exception as e:
        print(f"Eventbrite internal API error: {e}")
    return event_ids


async def _search_via_html(city: str = "chennai", category: str = "business") -> List[str]:
    """
    Fallback: Fetch Eventbrite search HTML page and parse event IDs from links.
    Uses aiohttp (no browser).
    """
    event_ids = []
    seen = set()
    search_url = f"{BASE_URL}/b/india--{city}/{category}/"
    try:
        timeout = aiohttp.ClientTimeout(total=25)
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(headers=BROWSER_HEADERS, timeout=timeout, connector=connector) as session:
            async with session.get(search_url) as resp:
                if resp.status != 200:
                    print(f"Eventbrite HTML search: status {resp.status}")
                    return []
                html = await resp.text()
                print(f"Eventbrite HTML: Got {len(html)} chars.")
                soup = BeautifulSoup(html, "lxml")
                # Extract event IDs from all links containing '-' followed by digits
                for tag in soup.find_all("a", href=True):
                    href = tag["href"]
                    if "/e/" in href or "eventbrite.com" in href:
                        parts = href.split("-")
                        if parts:
                            last = parts[-1].split("?")[0].strip("/")
                            if last.isdigit() and last not in seen:
                                seen.add(last)
                                event_ids.append(last)
                print(f"Eventbrite HTML: Found {len(event_ids)} event IDs.")
    except Exception as e:
        print(f"Eventbrite HTML search error: {e}")
    return event_ids


async def scrape_events_playwright(city: str = "chennai", category: str = "business") -> List[Dict]:
    """
    Main entry point. Uses HTTP-only strategy — no Playwright browser needed.
    """
    print(f"Eventbrite Scraper (HTTP): Starting for city={city}, category={category}")
    cleaned_events = []
    seen_ids = set()

    # 1. Try internal JSON API first
    event_ids = await _search_via_api(city, category)

    # 2. Fallback to HTML parsing
    if not event_ids:
        print("Eventbrite: Internal API returned 0 IDs. Trying HTML fallback...")
        event_ids = await _search_via_html(city, category)

    print(f"Eventbrite: Processing {len(event_ids)} event IDs via public API...")

    for event_id in event_ids[:25]:  # Cap at 25 to avoid hitting rate limits
        if event_id in seen_ids:
            continue
        seen_ids.add(event_id)

        print(f"Fetching API details for ID: {event_id}...")
        api_data = fetch_event_details_api(event_id)

        if api_data:
            event_data = {
                "eventbrite_id": event_id,
                "title": api_data["title"],
                "description": api_data["description"] or f"Eventbrite event in {city}",
                "start_time": api_data["start_time"],
                "end_time": api_data["end_time"],
                "url": api_data["url"],
                "image_url": api_data["logo_url"],
                "venue_name": api_data["venue_name"],
                "venue_address": api_data["venue_address"],
                "organizer_name": api_data["organizer_name"],
                "is_free": api_data["is_free"],
                "online_event": api_data["online_event"],
                "raw_data": {"source": "eventbrite_api"}
            }
            cleaned_events.append(event_data)
            if not is_business_event(event_data):
                print(f"  [Note] Weak keywords but passing: {event_data['title']}")
        else:
            print(f"Skipping {event_id} — API call failed.")

        # Small delay to avoid rate limiting
        await asyncio.sleep(0.3)

    print(f"Eventbrite Scraper: Collected {len(cleaned_events)} events.")
    return cleaned_events


def scrape_and_process_events(city: str):
    return asyncio.run(scrape_events_playwright(city))
