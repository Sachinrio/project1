import asyncio
import asyncpg
import os
from dotenv import load_dotenv
# Get DB URL from app config
from app.core.database import DATABASE_URL

load_dotenv()

async def patch_database():
    # Use the DATABASE_URL from our core config, but strip the +asyncpg for the raw asyncpg driver
    conn_str = DATABASE_URL
    if "+asyncpg" in conn_str:
        conn_str = conn_str.replace("+asyncpg", "")
    elif conn_str.startswith("postgres://"):
        conn_str = conn_str.replace("postgres://", "postgresql://", 1)
        
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
