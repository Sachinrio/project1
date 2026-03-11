from fastapi import APIRouter, HTTPException, Security
from pydantic import BaseModel, EmailStr
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
import os
import tempfile
from dotenv import load_dotenv
from typing import List

router = APIRouter()

load_dotenv()

# --- VALIDATION SCHEMA ---
class ContactForm(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    message: str

class ProposalForm(BaseModel):
    company_name: str
    contact_person: str
    email: EmailStr
    contact_number: str
    pdf_base64: str

# --- EMAIL CONFIGURATION ---
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS") == "True",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS") == "True",
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

@router.post("/contact")
async def send_contact_email(form_data: ContactForm):
    """
    Receives contact form submission and sends an email to the admin.
    """
    try:
        # Construct the email body
        html = f"""
        <h3>New Contact Form Submission</h3>
        <p><strong>Name:</strong> {form_data.first_name} {form_data.last_name}</p>
        <p><strong>Email:</strong> {form_data.email}</p>
        <p><strong>Message:</strong></p>
        <p>{form_data.message}</p>
        <hr>
        <p><em>Reply directly to this email to contact the user (Reply-To is set).</em></p>
        """

        # Prepare the message
        message = MessageSchema(
            subject=f"Infinite BZ Contact: {form_data.first_name} {form_data.last_name}",
            recipients=[os.getenv("MAIL_USERNAME")],  # Send TO the admin
            body=html,
            subtype=MessageType.html,
            reply_to=[form_data.email] # Set Reply-To to the user's email
        )

        # Send the email
        fm = FastMail(conf)
        await fm.send_message(message)

        return {"message": "Email sent successfully"}

    except Exception as e:
        print(f"EMAIL ERROR: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")

@router.post("/proposal/send")
async def send_proposal_email(form_data: ProposalForm):
    """
    Receives proposal details and PDF base64 string, sends it to admin and client.
    """
    import base64
    try:
        # Extract base64 content
        # Check if the base64 string contains the data URI prefix and split it
        pdf_data = form_data.pdf_base64
        if "base64," in pdf_data:
            pdf_data = pdf_data.split("base64,")[1]
            
        pdf_bytes = base64.b64decode(pdf_data)

        # Construct the client email body
        client_html = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f9fafb; padding: 20px; border-radius: 12px;">
            <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 5px solid #4f46e5;">
                <h3 style="color: #1f2937; font-size: 18px; margin-top: 0;">Hi {form_data.contact_person},</h3>
                <p style="color: #4b5563; line-height: 1.6;">Thank you for considering Infinite BZ as your technology partner.</p>
                <p style="color: #4b5563; line-height: 1.6;">Please find attached a comprehensive proposal tailored to your requirements, detailing our execution plan, innovation strategy, and value-driven solutions.</p>
                <p style="color: #4b5563; line-height: 1.6; margin-bottom: 25px;">We look forward to building something impactful together.</p>
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    <p style="color: #6b7280; font-size: 14px; margin-bottom: 5px;">Sincerely,</p>
                    <p style="color: #111827; font-weight: bold; margin-top: 0;">The Infinite BZ Team</p>
                </div>
            </div>
        </div>
        """

        # Construct the admin email body
        admin_html = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f3f4f6; padding: 20px;">
            <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; border-top: 5px solid #c026d3; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <h2 style="color: #111827; margin-top: 0; font-size: 20px;">New Proposal Generated</h2>
                <p style="color: #4b5563; margin-bottom: 25px;">A new lead has generated a proposal via the website calculator. Their exact quote is attached.</p>
                
                <h4 style="color: #4f46e5; margin-bottom: 10px; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; text-transform: uppercase; font-size: 12px; letter-spacing: 1px;">Client Details</h4>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <tr><td style="padding: 10px 0; border-bottom: 1px solid #f3f4f6; color: #6b7280; width: 40%;"><strong>Company / Business:</strong></td><td style="padding: 10px 0; border-bottom: 1px solid #f3f4f6; color: #111827;">{form_data.company_name}</td></tr>
                    <tr><td style="padding: 10px 0; border-bottom: 1px solid #f3f4f6; color: #6b7280;"><strong>Contact Person:</strong></td><td style="padding: 10px 0; border-bottom: 1px solid #f3f4f6; color: #111827;">{form_data.contact_person}</td></tr>
                    <tr><td style="padding: 10px 0; border-bottom: 1px solid #f3f4f6; color: #6b7280;"><strong>Email:</strong></td><td style="padding: 10px 0; border-bottom: 1px solid #f3f4f6; color: #111827;"><a href="mailto:{form_data.email}" style="color: #4f46e5; text-decoration: none;">{form_data.email}</a></td></tr>
                    <tr><td style="padding: 10px 0; border-bottom: 1px solid #f3f4f6; color: #6b7280;"><strong>Phone Number:</strong></td><td style="padding: 10px 0; border-bottom: 1px solid #f3f4f6; color: #111827;">{form_data.contact_number}</td></tr>
                </table>
                
                <p style="color: #9ca3af; font-size: 12px; text-align: center; margin-top: 30px;">This is an automated message from your Infinite BZ Application.</p>
            </div>
        </div>
        """

        admin_email = os.getenv("MAIL_USERNAME")
        if not admin_email:
            raise ValueError("MAIL_USERNAME environment variable is not set")

        # Save bytes to a temporary file for fastmail to attach
        filename = f"{form_data.company_name.replace(' ', '_')}_Proposal.pdf"
        
        # Create a temporary file and write the PDF bytes
        fd, temp_path = tempfile.mkstemp(suffix=".pdf")
        with os.fdopen(fd, 'wb') as f:
            f.write(pdf_bytes)

        try:
            fm = FastMail(conf)
            
            # 1. Prepare and send the client message
            client_message = MessageSchema(
                subject=f"Infinite BZ Proposal: {form_data.company_name}",
                recipients=[form_data.email],          # Send TO the client
                body=client_html,
                subtype=MessageType.html,
                attachments=[temp_path]                # Attach the physical file
            )
            await fm.send_message(client_message)

            # 2. Prepare and send the admin message
            admin_message = MessageSchema(
                subject=f"New Lead - Infinite BZ Proposal: {form_data.company_name}",
                recipients=[admin_email],              # Send TO the admin
                body=admin_html,
                subtype=MessageType.html,
                attachments=[temp_path]                # Attach the physical file
            )
            await fm.send_message(admin_message)
            
        finally:
            # Clean up the temporary file immediately after sending
            try:
                os.unlink(temp_path)
            except Exception as e:
                print(f"Could not delete temp PDF file {temp_path}: {e}")

        return {"message": "Proposal email sent successfully with attachment"}

    except Exception as e:
        print(f"PROPOSAL EMAIL ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to send proposal email")
