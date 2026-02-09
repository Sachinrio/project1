import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import urllib.parse

# --- CONSTANTS ---
BASE_URL = "https://www.eventbrite.com"

async def scrape_events_playwright(city: str = "chennai", category: str = "business--events") -> List[Dict]:
    """
    Scrapes Eventbrite for events in a specific city and category using Playwright.
    Returns a list of dictionaries matching the database schema.
    """
    cleaned_events = []
    
    # Construct Search URL
    # Example: https://www.eventbrite.com/d/india--chennai/business--events/
    # Ensure city is URL-safe
    encoded_city = urllib.parse.quote(city)
    search_url = f"{BASE_URL}/d/india--{encoded_city}/{category}/"
    
    print(f"🕵️‍♀️ Scraper: Starting Playwright session for {search_url}...")

    async with async_playwright() as p:
        # Launch browser (headless=True for background, False for debug)
        browser = await p.chromium.launch(headless=True)
        
        # Create a context with user-agent to avoid immediate bot detection
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            await page.goto(search_url, timeout=60000)
            
            # Wait for event cards to load
            await page.wait_for_selector("div.event-card__details, section.event-card-details", timeout=15000)
            
            # Scroll a bit to load more (lazy loading)
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, 1000)")
                await asyncio.sleep(random.uniform(1, 3))

            # HTML Parsing with BeautifulSoup
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            
            # Eventbrite's classes change often, so we try multiple common selectors
            # Currently: section.event-card-details is common for search results
            cards = soup.select("section.event-card-details, div.event-card__details")
            
            print(f"🔎 Found {len(cards)} raw cards. Parsing...")

            for card in cards:
                try:
                    # 1. Title
                    title_tag = card.select_one("h3, h2, .event-card__title")
                    title = title_tag.get_text(strip=True) if title_tag else "Untitled Event"
                    
                    # 2. Link & ID
                    link_tag = card.select_one("a.event-card-link, a")
                    url = link_tag['href'] if link_tag else ""
                    if url.startswith("/"):
                        url = BASE_URL + url
                    
                    # Extract ID from URL (e.g., .../e/my-event-1234567?aff=...)
                    # Fallback to random if not found (just for safety, usually present)
                    event_id = "unknown"
                    if "/e/" in url:
                        # simple extraction
                        parts = url.split("-")
                        last_part = parts[-1].split("?")[0]
                        if last_part.isdigit():
                            event_id = last_part
                    
                    if not event_id or event_id == "unknown":
                         continue # Skip invalid ones

                    # 3. Date
                    # Date is often in a specific format like "Tue, Dec 26, 7:00 PM"
                    date_tag = card.select_one("p:first-of-type, .event-card__date")
                    date_str = date_tag.get_text(strip=True) if date_tag else None
                    
                    # Parse Date (Simplified for MVP - uses current time + heuristic or raw string)
                    # For a robust app, use `dateparser` library
                    start_time = datetime.now() # Fallback
                    
                    # 4. Image
                    # Usually in a separate container, might be hard to get from 'card' element if strict hierarchy isn't preserved in finding.
                    # We often need to look at the parent 'article' or 'div' for the image
                    # For now, let's assume no image or try finding img tag
                    img_tag = card.find_previous("img") # This is risky, but works if structure is linear
                    image_url = img_tag['src'] if img_tag else None

                    # 5. Price
                    price_tag = card.select_one(".event-card__price")
                    is_free = False
                    if price_tag and "free" in price_tag.get_text().lower():
                        is_free = True

                    # 6. Location
                    location = city # Default
                    
                    cleaned_events.append({
                        "eventbrite_id": event_id,
                        "title": title,
                        "description": f"Scraped from {url}",
                        "start_time": start_time, # Needs proper parsing in v2
                        "end_time": start_time + timedelta(hours=2),
                        "url": url,
                        "image_url": image_url,
                        "venue_name": location,
                        "is_free": is_free,
                        "raw_data": {"original_date": date_str}
                    })

                except Exception as e:
                    print(f"⚠️ Error parsing card: {e}")
                    continue

        except Exception as e:
            print(f"❌ Scraper Error: {e}")
        
        finally:
            await browser.close()
            
    print(f"✅ Scraper finished. Parsed {len(cleaned_events)} events.")
    return cleaned_events

# Wrapper for synchronous calls if needed (though FastAPI handles async well)
def scrape_and_process_events(city: str):
    return asyncio.run(scrape_events_playwright(city))
