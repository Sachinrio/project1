import os
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def reset_onboarding():
    print("Resetting Onboarding Status...")
    async with engine.begin() as conn:
        try:
            # Target specific user or all for testing
            # Using the email seen in screenshots: pradeepshanmugaraj007@gmail.com
            email = "pradeepshanmugaraj007@gmail.com"
            
            # Check current status
            result = await conn.execute(text("SELECT razorpay_account_id FROM \"user\" WHERE email = :email"), {"email": email})
            row = result.fetchone()
            
            if row:
                print(f"Current ID for {email}: {row[0]}")
            else:
                print(f"User {email} not found.")

            # Clear the ID
            await conn.execute(text("UPDATE \"user\" SET razorpay_account_id = NULL WHERE email = :email"), {"email": email})
            print(f"SUCCESS: Cleared razorpay_account_id for {email}.")
            
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    import sys
    # Windows loop policy fix
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    asyncio.run(reset_onboarding())
