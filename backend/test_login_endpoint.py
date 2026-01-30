
import requests
url = "http://127.0.0.1:8000/api/v1/auth/login"
data = {"username": "test@example.com", "password": "wrongpassword"}
try:
    response = requests.post(url, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
