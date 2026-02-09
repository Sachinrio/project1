
import sys
print("Hello world")
try:
    from app.core.database import DATABASE_URL
    print(f"DB URL length: {len(DATABASE_URL)}")
    import asyncio
    print("Asyncio imported")
    from app.services.scraper import scrape_events_playwright
    print("Scraper imported")
except Exception as e:
    print(f"Error: {e}")
