import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_data():
    # Force Render URL from .env (which we modified locally)
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not set in .env")
        return

    # Cleaning URL for psycopg2 (remove +asyncpg)
    if "+asyncpg" in db_url:
        db_url = db_url.replace("+asyncpg", "")
    
    print(f"Connecting to: {db_url.split('@')[1] if '@' in db_url else '...'}")
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check Total
        cur.execute("SELECT count(*) FROM event;")
        count = cur.fetchone()[0]
        print(f"Total Events in DB: {count}")

        if count > 0:
            print("\nEvents by Source:")
            try:
                cur.execute("SELECT raw_data->>'source', count(*) FROM event GROUP BY raw_data->>'source';")
                for row in cur.fetchall():
                    print(f" - {row[0]}: {row[1]}")
            except Exception as e:
                print(f"Error grouping: {e}")

            print("\nLatest 5 Events (ID | Title | Start | Address):")
            cur.execute("SELECT id, title, start_time, venue_address FROM event ORDER BY created_at DESC LIMIT 5;")
            for row in cur.fetchall():
                print(f" - [{row[0]}] {row[1]} ({row[2]}) | {row[3]}")
        else:
            print("\nWARNING: Database is empty!")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    check_data()
