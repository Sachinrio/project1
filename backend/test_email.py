import asyncio
from app.core.email_utils import send_ticket_email, send_organizer_notification_email

async def main():
    print("Testing send_ticket_email...")
    res = await send_ticket_email(
        email="sachinsrmrmps@gmail.com",
        name="Test User",
        event_title="Test Event from Script",
        event_id=176,
        ticket_id="TEST-1234"
    )
    print(f"Result: {res}")

if __name__ == "__main__":
    asyncio.run(main())
