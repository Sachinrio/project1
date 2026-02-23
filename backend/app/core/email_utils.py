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
import resend
import asyncio

load_dotenv() # Load variables from .env file

# Configuration: Read from Environment Variables
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
resend.api_key = RESEND_API_KEY

# Use the configured Mail From or fallback to Resend's testing domain
MAIL_FROM = os.getenv("MAIL_FROM") or os.getenv("RESEND_FROM") or "onboarding@resend.dev"

ENABLE_EMAIL = bool(RESEND_API_KEY and RESEND_API_KEY.startswith("re_"))

if not ENABLE_EMAIL:
    print("WARNING: RESEND_API_KEY is missing or invalid in .env. Email processing is DISABLED.")
else:
    print(f"INFO: Resend API initialized. Sending emails FROM: {MAIL_FROM}")

async def send_reset_email(email: EmailStr, otp: str):
    """
    Sends the reset OTP via Real SMTP.
    """
    if not ENABLE_EMAIL:
        print(f"FAILED TO SEND EMAIL to {email}: Email credentials not configured.")
        return False

    print(f"Sending OTP email to {email} via {MAIL_SERVER}...")
    try:
        params = {
            "from": MAIL_FROM,
            "to": [email],
            "subject": "Password Reset Request - Infinite BZ",
            "html": f"""
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
        }
        await asyncio.to_thread(resend.Emails.send, params)
        print("Email sent successfully via Resend.")
        return True
    except Exception as e:
        print(f"EXTREME ERROR: Failed to send email via SMTP: {e}")
        return False

async def send_verification_email(email: EmailStr, otp: str):
    """
    Sends the verification OTP via Real SMTP.
    """
    if not ENABLE_EMAIL:
        print(f"FAILED TO SEND EMAIL to {email}: Email credentials not configured.")
        return False

    print(f"Sending Verification OTP to {email} via {MAIL_SERVER}...")
    try:
        params = {
            "from": MAIL_FROM,
            "to": [email],
            "subject": "Verify your email - Infinite BZ",
            "html": f"""
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
        }
        await asyncio.to_thread(resend.Emails.send, params)
        print("Verification email sent successfully via Resend.")
        return True
    except Exception as e:
        print(f"EXTREME ERROR: Failed to send email via SMTP: {e}")
        return False

async def send_ticket_email(email: EmailStr, name: str, event_title: str, event_id: int, ticket_id: str = ""):
    """
    Sends the Ticket Email via Real SMTP using fastapi-mail.
    """
    if not ENABLE_EMAIL:
        print(f"FAILED TO SEND TICKET to {email}: Email credentials not configured.")
        return False

    print(f"Sending Ticket to {email} via {MAIL_SERVER}...")
    try:
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #0F172A;">Successfully Registered: {event_title}</h2>
                    <p>Hi {name},</p>
                    <p>Thank you for registering! We are excited to see you.</p>
                    <br/>
                    <div style="text-align: center;">
                        <a href="http://localhost:5174/?view=ticket-details&eventId={event_id}&email={email}&ticketId={ticket_id}&eventName={quote(event_title)}" style="background-color: #38BDF8; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; border-radius: 5px;">Go to Ticket</a>
                    </div>
                    <br/>
                    <p style="font-size: 12px; color: #888;">Powered by Infinite BZ Event Platform</p>
                </div>
            </body>
        </html>
        """
        
        params = {
            "from": MAIL_FROM,
            "to": [email],
            "subject": f"Successfully Registered: {event_title}",
            "html": body
        }
        await asyncio.to_thread(resend.Emails.send, params)
        print("Ticket Email sent successfully via Resend.")
        return True
    except Exception as e:
        print(f"EXTREME ERROR: Failed to send ticket email via SMTP: {e}")
        return False

async def send_organizer_notification_email(email: EmailStr, organizer_name: str, attendee_name: str, attendee_email: str, event_title: str, event_date, ticket_path: str):
    """
    Sends a notification email to the organizer/admin (MAIL_FROM) about a new registration.
    """
    if not ENABLE_EMAIL:
        return False

    # Target the configured sender email (MAIL_FROM) or the specific organizer email passed in
    # The user said "mail from email id" which implies the sender address.
    recipient = MAIL_FROM 
    
    print(f"Sending Notification to {recipient} regarding {attendee_email}...")
    try:
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
        
        # Read the generated ticket PDF for the attachment
        with open(ticket_path, "rb") as f:
            pdf_bytes = f.read()

        params = {
            "from": MAIL_FROM,
            "to": [recipient],
            "subject": f"New Registration: {event_title} - {attendee_name}",
            "html": body,
            "attachments": [
                {
                    "filename": f"Ticket_{attendee_name.replace(' ', '_')}.pdf",
                    "content": list(pdf_bytes)
                }
            ]
        }
        
        await asyncio.to_thread(resend.Emails.send, params)
        print("Organizer notification sent via Resend.")
        return True
    except Exception as e:
        print(f"Failed to send organizer notification: {e}")
        return False
def generate_qr_code(data: str) -> str:
    """
    Generate QR code for given data and return as base64 string.
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def generate_event_ticket_pdf(event_data: dict, qr_base64: str, user_email: str, unique_ticket_id: str, user_name: str = None) -> BytesIO:
    """
    Generate a beautifully styled vertical PDF ticket with InfiniteBZ branding and professional design.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(400, 600))  # Vertical layout - one page
    width, height = 400, 600

    # White background
    c.setFillColorRGB(1, 1, 1)  # White
    c.rect(0, 0, width, height, fill=1)

    # Header with InfiniteBZ branding and primary color (#148EAB)
    c.setFillColorRGB(0.08, 0.55, 0.67)  # #148EAB equivalent
    c.rect(0, height-120, width, 120, fill=1)

    # InfiniteBZ icon and name - attractive design
    c.setFillColorRGB(1, 1, 1)  # White text
    c.setFont("Helvetica-Bold", 28)
    c.drawString(30, height - 50, "🎫 INFINITE BZ")
    c.setFont("Helvetica", 14)
    c.drawString(30, height - 75, "Event Management")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, height - 100, "SYSTEM")

    # Ticket ID section with primary color border
    c.setStrokeColorRGB(0.08, 0.55, 0.67)  # #148EAB border
    c.setLineWidth(3)
    c.roundRect(20, height-160, width-40, 35, 8)

    c.setFillColorRGB(0.08, 0.55, 0.67)  # Primary color text
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 145, f"TICKET ID: {unique_ticket_id}")

    # Event details in vertical layout
    y_pos = height - 200

    # Event Title
    c.setFillColorRGB(0.2, 0.2, 0.2)  # Dark gray
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, y_pos, "EVENT DETAILS")
    y_pos -= 30

    # Event Name
    c.setFillColorRGB(0.08, 0.55, 0.67)  # Primary color label
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y_pos, "Event Name:")
    c.setFillColorRGB(0.1, 0.1, 0.1)  # Dark text
    c.setFont("Helvetica", 11)
    event_title = event_data.get('title', 'N/A')
    c.drawString(120, y_pos, event_title[:25])
    y_pos -= 25

    # Date & Time
    c.setFillColorRGB(0.08, 0.55, 0.67)  # Primary color label
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y_pos, "Date & Time:")
    c.setFillColorRGB(0.1, 0.1, 0.1)  # Dark text
    c.setFont("Helvetica", 11)
    date_time = event_data.get('start_time', 'N/A')
    c.drawString(120, y_pos, date_time)
    y_pos -= 25

    # Venue
    c.setFillColorRGB(0.08, 0.55, 0.67)  # Primary color label
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y_pos, "Venue:")
    c.setFillColorRGB(0.1, 0.1, 0.1)  # Dark text
    c.setFont("Helvetica", 11)
    venue = event_data.get('venue_name', 'Online Event')
    c.drawString(85, y_pos, venue[:25])
    y_pos -= 25

    # Organizer
    c.setFillColorRGB(0.08, 0.55, 0.67)  # Primary color label
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y_pos, "Organizer:")
    c.setFillColorRGB(0.1, 0.1, 0.1)  # Dark text
    c.setFont("Helvetica", 11)
    organizer = event_data.get('organizer_name', 'InfiniteBZ')
    c.drawString(105, y_pos, organizer[:20])
    y_pos -= 25

    # Attendee
    c.setFillColorRGB(0.08, 0.55, 0.67)  # Primary color label
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y_pos, "Attendee Name:")
    c.setFillColorRGB(0.1, 0.1, 0.1)  # Dark text
    c.setFont("Helvetica", 11)
    display_name = user_name if user_name else user_email
    c.drawString(130, y_pos, display_name[:30])
    y_pos -= 40

    # QR Code section
    c.setFillColorRGB(0.95, 0.95, 0.95)  # Light gray background
    c.setStrokeColorRGB(0.08, 0.55, 0.67)  # Primary color border
    c.setLineWidth(2)
    c.roundRect(30, y_pos-180, width-60, 170, 10, fill=1)

    # QR Code title
    c.setFillColorRGB(0.08, 0.55, 0.67)  # Primary color
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width/2, y_pos-5, "SCAN FOR VERIFICATION")

    # QR Code
    if qr_base64:
        qr_img_data = base64.b64decode(qr_base64)
        qr_img = ImageReader(BytesIO(qr_img_data))
        c.drawImage(qr_img, 50, y_pos-160, width=120, height=120)

    # Terms and conditions
    terms_y = y_pos - 200
    c.setFillColorRGB(0.4, 0.4, 0.4)  # Gray text
    c.setFont("Helvetica", 8)
    c.drawString(30, terms_y, "• This ticket is non-transferable")
    c.drawString(30, terms_y - 12, "• Valid only for the registered attendee")
    c.drawString(30, terms_y - 24, "• Please arrive 30 minutes early")
    c.drawString(30, terms_y - 36, "• Keep this ticket safe")

    # Footer with InfiniteBZ branding
    c.setFillColorRGB(0.08, 0.55, 0.67)  # Primary color
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2 + 20, 30, "Thank you for using InfiniteBZ!")
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2 + 20, 15, "Event Management System")

    c.save()
    buffer.seek(0)
    return buffer

async def send_event_ticket_email(email: EmailStr, event_data: dict, confirmation_id: str = None, user_name: str = None):
    """
    Generate QR code and ticket PDF, then send email with attachments.
    """
    if not ENABLE_EMAIL:
        print(f"FAILED TO SEND EMAIL to {email}: Email credentials not configured.")
        return False

    temp_file_path = None
    try:
        print(f"Attempting to send ticket email to {email} using {MAIL_SERVER}:{MAIL_PORT} with user {MAIL_USERNAME}")

        # Generate unique ticket number
        import uuid
        import time
        unique_ticket_id = f"IBZ-{int(time.time())}-{str(uuid.uuid4())[:8].upper()}"

        # Generate QR code data with unique ticket number
        qr_data = f"Ticket ID: {unique_ticket_id}\nEvent: {event_data.get('title', 'N/A')}\nUser: {email}\nValid: {event_data.get('start_time', 'N/A')}"
        qr_base64 = generate_qr_code(qr_data)

        # Generate ticket PDF with confirmation ID (use the passed confirmation_id or unique_ticket_id as fallback)
        ticket_id_to_use = confirmation_id or unique_ticket_id
        pdf_buffer = generate_event_ticket_pdf(event_data, qr_base64, email, ticket_id_to_use, user_name)

        # Save PDF to temporary file
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_buffer.getvalue())
            temp_file_path = temp_file.name

        pdf_bytes = pdf_buffer.getvalue()

        params = {
            "from": MAIL_FROM,
            "to": [email],
            "subject": f"Your Event Ticket for {event_data.get('title', 'Event')}",
            "html": f"""
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
                            <a href="http://localhost:5174/?view=ticket-details&eventId={event_data.get('id', '')}&email={email}&ticketId={ticket_id_to_use}&eventName={quote(event_data.get('title', ''))}" style="background-color: #38BDF8; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; border-radius: 5px;">Go to Ticket</a>
                        </div>
                        <p style="font-size: 12px; color: #888;">Please bring this to the event.</p>
                    </div>
                </body>
            </html>
            """,
            "attachments": [
                {
                    "filename": f"{event_data.get('title', 'event').replace(' ', '_')}_ticket.pdf",
                    "content": list(pdf_bytes)
                }
            ]
        }
        
        await asyncio.to_thread(resend.Emails.send, params)
        print("Event ticket email sent successfully via Resend.")
        return True
    except Exception as e:
        print(f"ERROR: Failed to send event ticket email via Resend: {e}")
        return False
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                print(f"Warning: Could not delete temp file {temp_file_path}: {e}")

