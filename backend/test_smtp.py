import smtplib
import os
import base64
import asyncio
from email.message import EmailMessage
from email.utils import formataddr
from dotenv import load_dotenv

load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT") or 587)
MAIL_FROM_NAME = "Infinite BZ"

def test_registration_email():
    email = "infinitetechai14@gmail.com" # Change to a different test email if you want
    name = "Test User"
    event_title = "InfiniteBZ Launch Event"
    
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                <h2 style="color: #0F172A;">Successfully Registered: {event_title}</h2>
                <p>Hi {name},</p>
                <p>Thank you for registering! We are excited to see you.</p>
                <br/>
                <div style="text-align: center;">
                    <a href="http://localhost:5174/?view=ticket-details&eventId=1&email={email}" style="background-color: #38BDF8; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; border-radius: 8px; font-weight: bold;">Go to Ticket Box</a>
                </div>
                <br/>
                <p style="font-size: 12px; color: #888;">Powered by Infinite BZ Event Platform</p>
            </div>
        </body>
    </html>
    """

    msg = EmailMessage()
    msg["Subject"] = f"Successfully Registered: {event_title}"
    msg["From"] = formataddr((MAIL_FROM_NAME, MAIL_FROM))
    msg["To"] = email
    msg.set_content("HTML Content")
    msg.add_alternative(body, subtype='html')

    try:
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
        print(f"SUCCESS: Registration email sent to {email}")
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    test_registration_email()
