from .base_scraper import BaseScraper
from playwright.async_api import Page
from datetime import datetime, timedelta
import dateparser
import hashlib

from .utils import is_business_event

class AllEventsScraper(BaseScraper):
    async def scrape(self, page: Page):
        print("Starting AllEvents Scrape (Business Only)...")
        target_url = "https://allevents.in/chennai/business"
        
        try:
            print("AllEvents: Navigating Direct (Proxy Disabled)...")
            # Use domcontentloaded to avoid hanging on blocked assets
            try:
                await page.goto(target_url, timeout=60000, wait_until="domcontentloaded")
            except Exception as e:
                print(f"AllEvents: Goto timeout/error: {e}")
            
            # Wait for body to ensure load
            try:
                await page.wait_for_selector('body', timeout=15000)
            except Exception as e:
                print(f"AllEvents: Body selector timeout. Proceeding anyway... {e}")
                pass
            
            print("AllEvents page loaded.")

            # === FAST BULK EXTRACTION VIA PAGE.EVALUATE ===
            # Instead of looping in Python with Playwright async calls (slow on Render),
            # we do all DOM extraction in one single JS call. Massively faster.
            raw_items = await page.evaluate("""
                () => {
                    const results = [];
                    
                    // Try all known AllEvents card selectors
                    let cards = Array.from(document.querySelectorAll('.event-card'));
                    if (!cards.length) cards = Array.from(document.querySelectorAll('li[data-link]'));
                    if (!cards.length) cards = Array.from(document.querySelectorAll('div.event-item'));

                    const limit = Math.min(cards.length, 30);
                    for (let i = 0; i < limit; i++) {
                        const item = cards[i];
                        try {
                            // Title
                            const titleEl = item.querySelector('.title') || item.querySelector('h3');
                            const title = titleEl ? titleEl.innerText.trim() : "Unknown Event";

                            // Link
                            const linkEl = item.querySelector('a');
                            const link = linkEl ? (linkEl.getAttribute('href') || '') : (item.getAttribute('data-link') || '');

                            // Time
                            const timeEl = item.querySelector('.time') || item.querySelector('.date');
                            const timeStr = timeEl ? timeEl.innerText.trim() : '';

                            // Venue
                            const venueEl = item.querySelector('.subtitle') || item.querySelector('.location');
                            const venue = venueEl ? venueEl.innerText.trim() : 'Chennai';

                            // Image - check multiple attributes
                            let image = '';
                            const imgEl = item.querySelector('img.banner-image-v3') ||
                                          item.querySelector('img[data-src*="banner"]') ||
                                          item.querySelector('img[src*="banner"]') ||
                                          item.querySelector('img');
                            if (imgEl) {
                                for (const attr of ['data-src', 'data-img', 'data-lazy-src', 'srcset', 'src']) {
                                    let val = imgEl.getAttribute(attr) || '';
                                    if (val) {
                                        let candidate = val.split(',')[0].split(' ')[0].trim();
                                        if (candidate.startsWith('//')) candidate = 'https:' + candidate;
                                        const bad = ['og-logo', 'logo.jpg', 'logo.png', 'placeholder', 'blank.gif', 'data:image'];
                                        if (candidate.startsWith('http') && !bad.some(b => candidate.toLowerCase().includes(b))) {
                                            image = candidate;
                                            break;
                                        }
                                    }
                                }
                            }

                            results.push({ title, link, timeStr, venue, image });
                        } catch(e) {}
                    }
                    return results;
                }
            """)
            
            print(f"Found {len(raw_items)} AllEvents items.")
            
            image_pool = [
                "https://images.unsplash.com/photo-1540575861501-7cf05a4b125a?q=80&w=1000&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1505373630103-89d00c2a5851?q=80&w=1000&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?q=80&w=1000&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?q=80&w=1000&auto=format&fit=crop"
            ]

            events = []
            for item in raw_items:
                try:
                    title = item.get("title", "Unknown Event")
                    link = item.get("link", "")
                    time_str = item.get("timeStr", "")
                    venue = item.get("venue", "Chennai")
                    event_image = item.get("image", "") or image_pool[abs(hash(title)) % len(image_pool)]

                    start_time = datetime.now() + timedelta(days=2)
                    if time_str:
                        clean_time = time_str.replace('\n', ' ').strip()
                        parsed = dateparser.parse(clean_time)
                        if parsed:
                            start_time = parsed

                    event_data = {
                        "title": title,
                        "description": f"Event on AllEvents: {title}",
                        "start_time": start_time,
                        "end_time": start_time + timedelta(hours=3),
                        "url": link,
                        "venue_name": venue,
                        "image_url": event_image,
                        "eventbrite_id": f"allevents-{hashlib.md5(link.split('?')[0].encode()).hexdigest()}",
                        "is_free": False,
                        "category": "Business",
                        "raw_data": {"source": "allevents"}
                    }
                    
                    if is_business_event(event_data):
                        events.append(event_data)
                    else:
                        print(f"  [Filtered] Non-business event: {title}")
                except Exception as e:
                    print(f"Error parsing AllEvents item: {e}")
                    continue
                    
            return events

        except Exception as e:
            print(f"AllEvents Scrape Failed: {e}")
            return []
