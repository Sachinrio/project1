
import asyncio
import sys
import os
from sqlalchemy import text
from app.core.database import engine

async def report():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    output = []
    async with engine.begin() as conn:
        output.append("=== INFINITE BZ FINAL SCRAPE REPORT ===")
        
        # Source Counts
        res = await conn.execute(text("SELECT raw_data->>'source' as src, count(*) FROM event GROUP BY 1"))
        output.append("\n--- Event Source Counts ---")
        for row in res:
            output.append(f"{row[0]}: {row[1]}")
            
        # Image Audit
        output.append("\n--- Image Quality Audit ---")
        res = await conn.execute(text("SELECT count(*) FROM event WHERE image_url LIKE '%og-logo%'"))
        output.append(f"Generic Logos (AllEvents og-logo): {res.scalar()}")
        
        res = await conn.execute(text("SELECT count(*) FROM event WHERE image_url LIKE '%cdn-ip.allevents.in%'"))
        output.append(f"High Quality Images (AllEvents cdn-ip): {res.scalar()}")
        
        res = await conn.execute(text("SELECT count(*) FROM event WHERE image_url LIKE '%img.evbuc.com%'"))
        output.append(f"High Quality Images (Eventbrite): {res.scalar()}")

        # Unsplash check
        res = await conn.execute(text("SELECT count(*) FROM event WHERE image_url LIKE '%unsplash.com%'"))
        output.append(f"Fallback Images (Unsplash): {res.scalar()}")

    with open("final_report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    print("Report saved to final_report.txt")

if __name__ == "__main__":
    asyncio.run(report())
