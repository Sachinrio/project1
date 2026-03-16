from fastapi import APIRouter, HTTPException, Security
from pydantic import BaseModel, EmailStr
from app.core.email_utils import send_sendgrid_email
import os
import tempfile
import base64
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
        <p><em>Reply directly to this email to contact the user.</em></p>
        """

        # Prepare the message
        recipients = os.getenv("MAIL_FROM") or "infinitetechai14@gmail.com"
        
        # Send the email
        success = await send_sendgrid_email(
            to_email=recipients,
            subject=f"Infinite BZ Contact: {form_data.first_name} {form_data.last_name}",
            html_part=html
        )

        if success:
            return {"message": "Email sent successfully"}
        else:
            raise Exception("SendGrid failed to send contact email")

    except Exception as e:
        print(f"EMAIL ERROR: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")

@router.post("/proposal/send")
async def send_proposal_email(form_data: ProposalForm):
    """
    Receives proposal details and PDF base64 string, sends it to admin and client.
    """
    try:
        # Extract base64 content
        pdf_data = form_data.pdf_base64
        if "base64," in pdf_data:
            pdf_data = pdf_data.split("base64,")[1]
            
        # Construct the client email body
        client_html = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f9fafb; padding: 20px; border-radius: 12px;">
            <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 5px solid #4f46e5;">
                <h3 style="color: #1f2937; font-size: 18px; margin-top: 0;">Hi {form_data.contact_person},</h3>
                <p style="color: #4b5563; line-height: 1.6;">Thank you for considering Infinite BZ as your technology partner.</p>
                <p style="color: #4b5563; line-height: 1.6;">Please find attached a comprehensive proposal tailored to your requirements.</p>
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
                <p><strong>Company:</strong> {form_data.company_name}</p>
                <p><strong>Contact:</strong> {form_data.contact_person}</p>
                <p><strong>Email:</strong> {form_data.email}</p>
                <p><strong>Phone:</strong> {form_data.contact_number}</p>
            </div>
        </div>
        """

        admin_email = os.getenv("MAIL_FROM") or "infinitetechai14@gmail.com"

        # Attachment format for our utility
        attachment = {
            "ContentType": "application/pdf",
            "Filename": f"{form_data.company_name.replace(' ', '_')}_Proposal.pdf",
            "Base64Content": pdf_data
        }

        # 1. Send to Client
        await send_sendgrid_email(
            to_email=form_data.email,
            subject=f"Infinite BZ Proposal: {form_data.company_name}",
            html_part=client_html,
            attachments=[attachment]
        )

        # 2. Send to Admin
        await send_sendgrid_email(
            to_email=admin_email,
            subject=f"New Lead - Infinite BZ Proposal: {form_data.company_name}",
            html_part=admin_html,
            attachments=[attachment]
        )

        return {"message": "Proposal email sent successfully with attachment"}

    except Exception as e:
        print(f"PROPOSAL EMAIL ERROR: {e}")
        raise HTTPException(status_code=500, detail="Failed to send proposal email")
