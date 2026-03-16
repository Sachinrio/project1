import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("MAILJET_API_KEY")
secret = os.getenv("MAILJET_API_SECRET")

print(f"Key loaded: '{key}'")
print(f"Secret loaded: '{secret}'")
