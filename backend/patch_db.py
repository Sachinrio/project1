import asyncio
import asyncpg

async def patch_database():
    # Connection strings from database.py
    # DATABASE_URL = "postgresql+asyncpg://postgres:12345@localhost:5432/events_hub"
    # we need the asyncpg version without the driver prefix for raw connection
    conn_str = "postgresql://postgres:12345@localhost:5432/events_hub"
    
    try:
        print(f"🔌 Connecting to {conn_str}...")
        conn = await asyncpg.connect(conn_str)
        
        print("🔨 Patching table 'userregistration'...")
        # Add column if it doesn't exist
        await conn.execute("""
            ALTER TABLE userregistration 
            ADD COLUMN IF NOT EXISTS confirmation_id VARCHAR;
        """)

        await conn.execute("""
            ALTER TABLE userregistration 
            ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'PENDING';
        """)

        print("🔨 Patching table 'event'...")
        await conn.execute("""
            ALTER TABLE event 
            ADD COLUMN IF NOT EXISTS category VARCHAR DEFAULT 'Business';
        """)

        await conn.execute("""
            ALTER TABLE event 
            ADD COLUMN IF NOT EXISTS capacity INTEGER;
        """)

        await conn.execute("""
            ALTER TABLE event 
            ADD COLUMN IF NOT EXISTS registration_deadline TIMESTAMP;
        """)

        await conn.execute("""
            ALTER TABLE event 
            ADD COLUMN IF NOT EXISTS meeting_link VARCHAR;
        """)

        await conn.execute("""
            ALTER TABLE event 
            ADD COLUMN IF NOT EXISTS meeting_link_private BOOLEAN DEFAULT TRUE;
        """)

        await conn.execute("""
            ALTER TABLE event 
            ADD COLUMN IF NOT EXISTS timezone VARCHAR DEFAULT 'UTC';
        """)
        
        print("✅ SUCCESS: Column 'confirmation_id' added!")
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(patch_database())
