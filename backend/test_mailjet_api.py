from mailjet_rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

def test_mailjet_api():
    api_key = os.getenv("MAILJET_API_KEY")
    api_secret = os.getenv("MAILJET_API_SECRET")
    mail_from = os.getenv("MAIL_FROM")

    print(f"Testing Mailjet API with Key: {api_key[:5]}...")
    
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
      'Messages': [
        {
          "From": {
            "Email": mail_from,
            "Name": "Infinite BZ"
          },
          "To": [
            {
              "Email": mail_from,
              "Name": "Test User"
            }
          ],
          "Subject": "Mailjet API Test",
          "TextPart": "Testing Mailjet REST API deliverability.",
          "HTMLPart": "<h3>Mailjet API Test</h3><p>Does this reach the inbox?</p>"
        }
      ]
    }
    result = mailjet.send.create(data=data)
    print(f"Status: {result.status_code}")
    print(f"JSON: {result.json()}")

if __name__ == "__main__":
    test_mailjet_api()
