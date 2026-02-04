import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/infinite_bz")
if "+asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")

def reset_onboarding_sync():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        email = "pradeepshanmugaraj007@gmail.com"
        print(f"Checking for user: {email}")
        
        # Check
        result = conn.execute(text("SELECT razorpay_account_id FROM \"user\" WHERE email = :email"), {"email": email})
        row = result.fetchone()
        
        if row:
            print(f"User found. Current ID: {row[0]}")
            # Update
            conn.execute(text("UPDATE \"user\" SET razorpay_account_id = NULL WHERE email = :email"), {"email": email})
            conn.commit()
            print("SUCCESS: Cleared razorpay_account_id directly.")
        else:
            print("User NOT found. Please check the email address.")

if __name__ == "__main__":
    try:
        reset_onboarding_sync()
    except Exception as e:
        print(f"FAILED: {e}")
