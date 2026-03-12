from pydantic import EmailStr
import os
from dotenv import load_dotenv
import qrcode
import base64
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import tempfile
from urllib.parse import quote
import asyncio
from mailjet_rest import Client

load_dotenv() # Load variables from .env file

# Configuration: Mailjet API Keys
MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
MAILJET_API_SECRET = os.getenv("MAILJET_API_SECRET")
MAIL_FROM = os.getenv("MAIL_FROM") or "sachinsrmrmps@gmail.com"
MAIL_FROM_NAME = "Infinite BZ"

mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')
ENABLE_EMAIL = True

async def send_mailjet_email(to_email: str, subject: str, html_part: str, attachments: list = None):
    """
    Core helper to send emails via Mailjet API v3.1
    """
    print(f"DEBUG: Attempting to send Mailjet email to {to_email}...")
    print(f"DEBUG: Using MAIL_FROM: {MAIL_FROM}")
    
    if not MAILJET_API_KEY or not MAILJET_API_SECRET:
        print("ERROR: Mailjet API keys are missing from environment.")
        return False

    data = {
      'Messages': [
        {
          "From": {
            "Email": MAIL_FROM,
            "Name": MAIL_FROM_NAME
          },
          "To": [
            {
              "Email": to_email,
              "Name": to_email
            }
          ],
          "Subject": subject,
          "HTMLPart": html_part,
          "CustomID": "InfiniteBZ"
        }
      ]
    }
    
    if attachments:
        data['Messages'][0]['Attachments'] = attachments

    try:
        result = await asyncio.to_thread(mailjet.send.create, data=data)
        if result.status_code == 200:
            print(f"SUCCESS: Mailjet accepted email to {to_email}")
            print(f"DEBUG: Mailjet Response Body: {result.json()}")
            return True
        else:
            print(f"MAILJET API FAILURE: Status {result.status_code}")
            print(f"DEBUG: Request Data sent: {data}")
            print(f"DEBUG: Error Response Body: {result.json()}")
            return False
    except Exception as e:
        print(f"EXCEPTION sending via Mailjet: {type(e).__name__}: {e}")
        return False

async def send_reset_email(email: EmailStr, otp: str):
    html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #333;">Password Reset</h2>
                    <p>You requested a password reset for Infinite BZ.</p>
                    <p>Your OTP code is:</p>
                    <h1 style="color: #22d3ee; font-size: 32px; letter-spacing: 5px;">{otp}</h1>
                    <p>This code expires in 10 minutes.</p>
                    <p style="font-size: 12px; color: #888;">If you didn't request this, please ignore this email.</p>
                </div>
            </body>
        </html>
    """
    return await send_mailjet_email(email, "Password Reset Request - Infinite BZ", html_content)

async def send_verification_email(email: EmailStr, otp: str):
    html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #333;">Email Verification</h2>
                    <p>Welcome to Infinite BZ! Please verify your email address.</p>
                    <p>Your verification code is:</p>
                    <h1 style="color: #22c55e; font-size: 32px; letter-spacing: 5px;">{otp}</h1>
                    <p>This code expires in 10 minutes.</p>
                    <p style="font-size: 12px; color: #888;">If you didn't request this, please ignore this email.</p>
                </div>
            </body>
        </html>
    """
    return await send_mailjet_email(email, "Verify your email - Infinite BZ", html_content)

async def send_ticket_email(email: EmailStr, name: str, event_title: str, event_id: int, ticket_id: str = "", ticket_path: str = None):
    attachments = []
    if ticket_path and os.path.exists(ticket_path):
        try:
            with open(ticket_path, "rb") as f:
                pdf_bytes = f.read()
            attachments.append({
                "ContentType": "application/pdf",
                "Filename": f"Ticket_{event_title.replace(' ', '_')}.pdf",
                "Base64Content": base64.b64encode(pdf_bytes).decode('utf-8')
            })
        except Exception as e:
            print(f"Error reading ticket for attachment: {e}")

    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                <h2 style="color: #0F172A;">Successfully Registered: {event_title}</h2>
                <p>Hi {name},</p>
                <p>Thank you for registering! We are excited to see you.</p>
                {"<p>Your ticket is attached to this email as a PDF.</p>" if ticket_path else ""}
                <br/>
                <div style="text-align: center;">
                    <a href="https://project1-y363.onrender.com/?view=ticket-details&eventId={event_id}&email={email}&ticketId={ticket_id}&eventName={quote(event_title)}" style="background-color: #38BDF8; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; border-radius: 5px;">Go to Ticket Box</a>
                </div>
                <br/>
                <p style="font-size: 12px; color: #888;">Powered by Infinite BZ Event Platform</p>
            </div>
        </body>
    </html>
    """
    return await send_mailjet_email(email, f"Successfully Registered: {event_title}", body, attachments=attachments)

async def send_organizer_notification_email(email: EmailStr, organizer_name: str, attendee_name: str, attendee_email: str, event_title: str, event_date, ticket_path: str):
    try:
        with open(ticket_path, "rb") as f:
            pdf_bytes = f.read()
        
        attachment = {
            "ContentType": "application/pdf",
            "Filename": f"Ticket_{attendee_name.replace(' ', '_')}.pdf",
            "Base64Content": base64.b64encode(pdf_bytes).decode('utf-8')
        }
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #0F172A;">New Registration for {event_title}</h2>
                    <p><strong>A new attendee has registered!</strong></p>
                    <hr/>
                    <p><strong>Event:</strong> {event_title}</p>
                    <p><strong>Organizer:</strong> {organizer_name}</p>
                    <p><strong>Date & Time:</strong> {event_date}</p>
                    <hr/>
                    <p><strong>Attendee Name:</strong> {attendee_name}</p>
                    <p><strong>Attendee Email:</strong> {attendee_email}</p>
                    <br/>
                    <p>The ticket PDF sent to the user is attached for your records.</p>
                </div>
            </body>
        </html>
        """
        # Recipient is the admin/MAIL_FROM
        return await send_mailjet_email(MAIL_FROM, f"New Registration: {event_title} - {attendee_name}", body, attachments=[attachment])
    except Exception as e:
        print(f"Error preparing organizer email: {e}")
        return False

def generate_qr_code(data: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def generate_event_ticket_pdf(event_data: dict, qr_base64: str, user_email: str, unique_ticket_id: str, user_name: str = None) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(400, 600))
    width, height = 400, 600
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, width, height, fill=1)
    c.setFillColorRGB(0.08, 0.55, 0.67)
    c.rect(0, height-120, width, 120, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(30, height - 50, "🎫 INFINITE BZ")
    c.setFont("Helvetica", 14)
    c.drawString(30, height - 75, "Event Management")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, height - 100, "SYSTEM")
    c.setStrokeColorRGB(0.08, 0.55, 0.67)
    c.setLineWidth(3)
    c.roundRect(20, height-160, width-40, 35, 8)
    c.setFillColorRGB(0.08, 0.55, 0.67)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 145, f"TICKET ID: {unique_ticket_id}")
    y_pos = height - 200
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, y_pos, "EVENT DETAILS")
    y_pos -= 30
    c.setFillColorRGB(0.08, 0.55, 0.67)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y_pos, "Event Name:")
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("Helvetica", 11)
    event_title = event_data.get('title', 'N/A')
    c.drawString(120, y_pos, event_title[:25])
    y_pos -= 25
    c.setFillColorRGB(0.08, 0.55, 0.67)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y_pos, "Date & Time:")
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("Helvetica", 11)
    date_time = str(event_data.get('start_time', 'N/A'))
    c.drawString(120, y_pos, date_time)
    y_pos -= 25
    c.setFillColorRGB(0.08, 0.55, 0.67)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y_pos, "Venue:")
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("Helvetica", 11)
    venue = event_data.get('venue_name', 'Online Event')
    c.drawString(85, y_pos, venue[:25])
    y_pos -= 25
    c.setFillColorRGB(0.08, 0.55, 0.67)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y_pos, "Organizer:")
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("Helvetica", 11)
    organizer = event_data.get('organizer_name', 'InfiniteBZ')
    c.drawString(105, y_pos, organizer[:20])
    y_pos -= 25
    c.setFillColorRGB(0.08, 0.55, 0.67)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y_pos, "Attendee Name:")
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("Helvetica", 11)
    name = user_name or user_email
    c.drawString(135, y_pos, name[:20])
    y_pos -= 30
    img_data = base64.b64decode(qr_base64)
    img = ImageReader(BytesIO(img_data))
    c.drawImage(img, (width-150)/2, y_pos-140, width=150, height=150)
    y_pos -= 160
    c.setFillColorRGB(0.08, 0.55, 0.67)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2, y_pos, "SCAN AT ENTRANCE")
    y_pos -= 30
    c.setDash(3, 3)
    c.line(20, y_pos, width-20, y_pos)
    y_pos -= 20
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, y_pos, "This is a computer generated ticket.")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

async def send_event_ticket_email(email: EmailStr, event_data: dict, confirmation_id: str = None, user_name: str = None):
    try:
        import uuid
        import time
        unique_ticket_id = confirmation_id or f"IBZ-{int(time.time())}-{str(uuid.uuid4())[:8].upper()}"
        qr_data = f"Ticket ID: {unique_ticket_id}\nEvent: {event_data.get('title', 'N/A')}\nUser: {email}"
        qr_base64 = generate_qr_code(qr_data)
        pdf_buffer = generate_event_ticket_pdf(event_data, qr_base64, email, unique_ticket_id, user_name)
        pdf_bytes = pdf_buffer.getvalue()
        
        attachment = {
            "ContentType": "application/pdf",
            "Filename": f"{event_data.get('title', 'event').replace(' ', '_')}_ticket.pdf",
            "Base64Content": base64.b64encode(pdf_bytes).decode('utf-8')
        }
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #333;">Event Registration Confirmed</h2>
                    <p>Thank you for registering for <strong>{event_data.get('title', 'the event')}</strong>.</p>
                    <p>Your event ticket is attached as a PDF. Please bring this ticket to the event.</p>
                    <p>You can also scan the QR code below:</p>
                    <img src="data:image/png;base64,{qr_base64}" alt="QR Code" style="max-width: 200px;" />
                    <br/>
                    <div style="text-align: center; margin-top: 20px;">
                        <a href="https://project1-y363.onrender.com/?view=ticket-details&eventId={event_data.get('id', '')}&email={email}&ticketId={unique_ticket_id}&eventName={quote(event_data.get('title', ''))}" style="background-color: #38BDF8; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; border-radius: 5px;">Go to Ticket</a>
                    </div>
                </div>
            </body>
        </html>
        """
        return await send_mailjet_email(email, f"Your Event Ticket for {event_data.get('title', 'Event')}", body, attachments=[attachment])
    except Exception as e:
        print(f"Error sending event ticket: {e}")
        return False
