from mailjet_rest import Client
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_mailjet_api_final():
    api_key = os.getenv("MAILJET_API_KEY")
    api_secret = os.getenv("MAILJET_API_SECRET")
    mail_from = os.getenv("MAIL_FROM")
    mail_from_name = "Infinite BZ"
    
    to_email = "infinitetechai14@gmail.com"
    
    print(f"Testing Mailjet API Final with Key: {api_key[:5]}...")
    
    client = Client(auth=(api_key, api_secret), version='v3.1')
    
    message = {
        "From": {
            "Email": mail_from,
            "Name": mail_from_name
        },
        "To": [
            {
                "Email": to_email,
                "Name": to_email.split('@')[0]
            }
        ],
        "Subject": "Final Mailjet API Delivery Test",
        "HTMLPart": "<h3>Success!</h3><p>The Mailjet REST API is working. Please check your inbox and spam folder.</p>"
    }

    data = { 'Messages': [message] }

    try:
        result = client.send.create(data=data)
        if result.status_code == 200:
            print(f"SUCCESS: Mailjet API sent email. Response: {result.json()}")
        else:
            print(f"ERROR: Mailjet API failed with status {result.status_code}: {result.json()}")
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    asyncio.run(test_mailjet_api_final())
