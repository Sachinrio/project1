import sendgrid
import os
import asyncio
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv
from python_http_client.exceptions import ForbiddenError

load_dotenv()

async def test_sendgrid_api_final():
    api_key = os.getenv("SENDGRID_API_KEY")
    mail_from = os.getenv("MAIL_FROM") or "infinitetechai14@gmail.com"
    mail_from_name = "Infinite BZ"
    
    to_email = "infinitetechai14@gmail.com"
    
    print(f"Testing SendGrid API Final with Key: {api_key[:10]}...")
    
    sg = sendgrid.SendGridAPIClient(api_key=api_key)
    from_email = Email(mail_from, mail_from_name)
    to_email_obj = To(to_email)
    subject = "Final SendGrid API Delivery Test"
    content = Content("text/html", "<h3>Success!</h3><p>The SendGrid API is worked. Please check your inbox.</p>")
    
    mail = Mail(from_email, to_email_obj, subject, content)

    try:
        response = await asyncio.to_thread(sg.send, mail)
        print(f"Status Code: {response.status_code}")
        print(f"Body: {response.body}")
        print(f"Headers: {response.headers}")
    except ForbiddenError as e:
        print(f"FORBIDDEN ERROR: {e}")
        print(f"ERROR BODY: {e.body}")
    except Exception as e:
        print(f"EXCEPTION: {type(e).__name__}: {e}")
        if hasattr(e, 'body'):
            print(f"ERROR BODY: {e.body}")

if __name__ == "__main__":
    asyncio.run(test_sendgrid_api_final())
