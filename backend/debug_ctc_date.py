
from bs4 import BeautifulSoup
import dateparser
import os
from datetime import datetime, timedelta

html_file = "ctc_debug.html"
with open(html_file, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

items = soup.select(".schedule-item")
print(f"Items: {len(items)}")

for item in items[:5]:
    date_el = item.select_one('li:has(i.fa-calendar)')
    date_text = date_el.get_text(strip=True) if date_el else "N/A"
    print(f"Date Text: '{date_text}'")
    
    start_time = dateparser.parse(date_text, settings={'DATE_ORDER': 'DMY', 'PREFER_DATES_FROM': 'future'})
    print(f"Parsed: {start_time}")
    
    if start_time:
        now = datetime.now()
        six_months_later = now + timedelta(days=180)
        print(f"Is Past? {start_time < now.replace(hour=0, minute=0, second=0)}")
        print(f"Is > 6 Months? {start_time > six_months_later}")
