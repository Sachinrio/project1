import requests

API_KEY = "732e2cd9fe4e164adf7ea5af96390f39"
API_SECRET = "854b11593301985a75c0243064a09353"
MAIL_FROM = "sachinsrmrmps@gmail.com"

data = {
  'Messages': [
    {
      "From": {
        "Email": MAIL_FROM,
        "Name": "Infinite BZ"
      },
      "To": [
        {
          "Email": "sachinsrmrmps@gmail.com",
          "Name": "Test"
        }
      ],
      "Subject": "Test Direct Request",
      "TextPart": "Hello",
      "HTMLPart": "<h1>Hello</h1>"
    }
  ]
}

response = requests.post(
    "https://api.mailjet.com/v3.1/send",
    auth=(API_KEY, API_SECRET),
    json=data
)

print(response.status_code)
print(response.json())
