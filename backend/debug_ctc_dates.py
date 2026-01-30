
import dateparser
from datetime import datetime

date_texts = [
    "13-Feb-2026 - 15-Feb-2026",
    "20-Feb-2026",
    "13 - 15 Feb 2026",
    "Feb 13, 2026"
]

for date_text in date_texts:
    print(f"\nTesting: '{date_text}'")
    
    # Logic in trade_centre.py
    parts = date_text.split("-")
    print(f"Split parts: {parts}")
    
    start_str = parts[0].strip() + "-" + parts[1].strip() + "-" + parts[2].strip() if len(parts) >= 3 else date_text
    print(f"Constructed start_str: '{start_str}'")
    
    start_time = dateparser.parse(date_text)
    print(f"Direct parse: {start_time}")
    
    if not start_time:
        start_time = dateparser.parse(start_str)
        print(f"Parse start_str: {start_time}")

    if not start_time:
        # Try splitting by ' - ' (with spaces)
        main_parts = date_text.split(" - ")
        if len(main_parts) > 0:
            start_time = dateparser.parse(main_parts[0])
            print(f"Parse main_parts[0]: {start_time}")
