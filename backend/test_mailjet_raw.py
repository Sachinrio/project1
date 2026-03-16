import asyncio
import os
from dotenv import load_dotenv
from mailjet_rest import Client

load_dotenv()

MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
MAILJET_API_SECRET = os.getenv("MAILJET_API_SECRET")
MAIL_FROM = os.getenv("MAIL_FROM") or "sachinsrmrmps@gmail.com"
MAIL_FROM_NAME = "Infinite BZ"

mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')

async def main():
    data = {
      'Messages': [
        {
          "From": {
            "Email": MAIL_FROM,
            "Name": MAIL_FROM_NAME
          },
          "To": [
            {
              "Email": "sachinrio74@gmail.com",
              "Name": "Sachin"
            }
          ],
          "Subject": "Test Direct Request from Script",
          "TextPart": "Hello out there",
          "HTMLPart": "<h1>Hello out there</h1>",
          "CustomID": "TestID"
        }
      ]
    }
    
    try:
        result = await asyncio.to_thread(mailjet.send.create, data=data)
        print("Status code:", result.status_code)
        print("Response:", result.json())
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    asyncio.run(main())
