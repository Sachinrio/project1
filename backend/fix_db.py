import os
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/infinite_bz")
# Enforce sync driver for this script
if "+asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")

def fix_database():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Connected.")
        
        # Check if column exists
        try:
            # We use text() for raw SQL
            # Note: "user" is a reserved word in Postgres, so we must quote it
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user' AND column_name='razorpay_account_id'"))
            exists = result.fetchone()
            
            if exists:
                print("SUCCESS: Column 'razorpay_account_id' ALREADY EXISTS.")
                return
            else:
                print("INFO: Column 'razorpay_account_id' is MISSING.")
        except Exception as e:
            print(f"Error checking column: {e}")

        # Add column if missing
        print("Attempting to ADD column...")
        try:
            conn.execute(text('ALTER TABLE "user" ADD COLUMN razorpay_account_id VARCHAR'))
            conn.commit()
            print("SUCCESS: Column 'razorpay_account_id' ADDED successfully.")
        except Exception as e:
            print(f"CRITICAL ERROR adding column: {e}")
            # Identify if it's because it already exists (race condition)
            if "already exists" in str(e):
                 print("Safe to ignore: Column already exists.")

if __name__ == "__main__":
    try:
        fix_database()
    except Exception as e:
        print(f"Script Failed: {e}")