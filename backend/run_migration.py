import asyncio
from sqlalchemy import text
from app.core.database import engine

async def migrate():
    async with engine.begin() as conn:
        print("Adding reset_otp column...")
        try:
            await conn.execute(text('ALTER TABLE "user" ADD COLUMN reset_otp VARCHAR'))
            print("Added reset_otp.")
        except Exception as e:
            print(f"Skipping reset_otp (maybe exists): {e}")
            
        print("Adding otp_expires_at column...")
        try:
            await conn.execute(text('ALTER TABLE "user" ADD COLUMN otp_expires_at TIMESTAMP WITHOUT TIME ZONE'))
            print("Added otp_expires_at.")
        except Exception as e:
            print(f"Skipping otp_expires_at (maybe exists): {e}")

if __name__ == "__main__":
    if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(migrate())
