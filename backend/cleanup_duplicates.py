
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def cleanup_duplicates():
    async with engine.connect() as conn:
        print("Scaning for duplicates (Title + Start Time)...")
        
        # Find duplicates
        stmt = text("""
            SELECT title, start_time, array_agg(id) as ids, count(*) 
            FROM event 
            GROUP BY title, start_time 
            HAVING count(*) > 1
        """)
        res = await conn.execute(stmt)
        groups = res.fetchall()
        
        if not groups:
            print("No duplicates found.")
            return

        print(f"Found {len(groups)} duplicate groups.")
        
        total_deleted = 0
        
        for row in groups:
            ids = row.ids
            # Keep the first one (or last, doesn't matter much for scraped data, usually latest is best but let's just keep one)
            # ids is a list. Let's keep the one with the smallest ID (oldest) or largest (newest)?
            # If we assume re-scrapes added new ones, maybe newest has better data? 
            # Or oldest has existing registrations? 
            # Safest is to keep the one that might have registrations.
            # But checking that is complex. 
            # Let's just keep the first one in the list.
            keep_id = ids[0]
            delete_ids = ids[1:]
            
            if not delete_ids:
                continue
                
            print(f"Group '{row.title}': Keeping {keep_id}, Deleting {delete_ids}")
            
            # Format duplicate IDs for SQL IN clause
            # tuple(delete_ids) might have 1 item which puts a comma (1,) which is valid sql
            # but empty tuple is invalid. We checked `if not delete_ids`.
            
            ids_tuple = tuple(delete_ids)
            
            # 1. Delete Registrations for these duplicates
            # Using text execution. Need to handle tuple formatting efficiently or loop.
            # Simple loop is safer for small batches.
            for bad_id in delete_ids:
                await conn.execute(text(f"DELETE FROM userregistration WHERE event_id = {bad_id}"))
                await conn.execute(text(f"DELETE FROM event WHERE id = {bad_id}"))
            
            total_deleted += len(delete_ids)
            
        await conn.commit()
        print(f"Cleanup Complete. Deleted {total_deleted} duplicate events.")

if __name__ == "__main__":
    asyncio.run(cleanup_duplicates())
