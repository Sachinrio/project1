
import sqlite3
import os
from sqlalchemy import create_engine, text

# Get DB URL from app config
from app.core.database import DATABASE_URL

# Convert asyncpg to psycopg2 for sync run
sync_url = DATABASE_URL
if "asyncpg" in sync_url:
    sync_url = sync_url.replace("asyncpg", "psycopg2")

engine = create_engine(sync_url)
with engine.connect() as conn:
    print("Force deleting all events and related data...")
    try:
        conn.execute(text("DELETE FROM userregistration"))
    except Exception as e:
        print(f"Error clearing userregistration: {e}")
        
    try:
        conn.execute(text("DELETE FROM ticketclass"))
    except Exception as e:
        print(f"Error clearing ticketclass: {e}")
        
    res = conn.execute(text("DELETE FROM event"))
    conn.commit()
    print(f"DONE. Deleted {res.rowcount} events.")
