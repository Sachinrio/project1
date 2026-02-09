
import psycopg2
from psycopg2 import sql

def patch_database():
    conn_str = "postgresql://postgres:12345@localhost:5432/events_hub"
    
    try:
        print(f"Connecting to {conn_str}...")
        conn = psycopg2.connect(conn_str)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Patching table 'userregistration'...")
        cur.execute("ALTER TABLE userregistration ADD COLUMN IF NOT EXISTS confirmation_id VARCHAR;")
        cur.execute("ALTER TABLE userregistration ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'PENDING';")

        print("Patching table 'event'...")
        cur.execute("ALTER TABLE event ADD COLUMN IF NOT EXISTS category VARCHAR DEFAULT 'Business';")
        cur.execute("ALTER TABLE event ADD COLUMN IF NOT EXISTS capacity INTEGER;")
        cur.execute("ALTER TABLE event ADD COLUMN IF NOT EXISTS registration_deadline TIMESTAMP;")
        cur.execute("ALTER TABLE event ADD COLUMN IF NOT EXISTS meeting_link VARCHAR;")
        cur.execute("ALTER TABLE event ADD COLUMN IF NOT EXISTS meeting_link_private BOOLEAN DEFAULT TRUE;")
        cur.execute("ALTER TABLE event ADD COLUMN IF NOT EXISTS timezone VARCHAR DEFAULT 'UTC';")
        
        print("Patching table 'user'...")
        cur.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS reset_otp VARCHAR;')
        cur.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS otp_expires_at TIMESTAMP;')
        # Profile Fields
        cur.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS first_name VARCHAR;')
        cur.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_name VARCHAR;')
        cur.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS job_title VARCHAR;')
        cur.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS company VARCHAR;')
        cur.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS phone VARCHAR;')
        cur.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS bio VARCHAR;')
        cur.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS profile_image VARCHAR;')
        
        print("SUCCESS: Schema updated successfully from sync script!")
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    patch_database()
