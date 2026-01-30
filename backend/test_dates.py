
from datetime import datetime
import dateparser

now = datetime.now()
print(f"NOW: {now}")

date_text = "13-Feb-2026"
parsed = dateparser.parse(date_text, settings={'DATE_ORDER': 'DMY', 'PREFER_DATES_FROM': 'future'})
print(f"PARSED: {parsed}")

print(f"PARSED < NOW? {parsed < now}")
