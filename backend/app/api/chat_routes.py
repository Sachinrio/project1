from fastapi import APIRouter, Depends, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from pydantic import BaseModel
import asyncio
from jose import jwt, JWTError
import os

from app.core.database import get_session
from app.models.schemas import User
from app.models.msme_schema import ChatSession, MSMERegistration
from app.auth import SECRET_KEY, ALGORITHM
import json

# Load NIC data
NIC_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "nic_data.json")
try:
    with open(NIC_DATA_PATH, "r") as f:
        NIC_DATA = json.load(f)
except Exception as e:
    print(f"Error loading NIC data: {e}")
    NIC_DATA = {"manufacturing": {}, "services": {}, "trading": {}}

router = APIRouter(tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    user_location: str = "Unknown"
    current_page: str = "Unknown"

async def get_optional_user(request: Request, session: AsyncSession) -> User | None:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            return None
        result = await session.execute(select(User).where(User.email == email))
        return result.scalars().first()
    except JWTError:
        return None
        

@router.post("/chat")
async def chat_interaction(
    req: ChatRequest,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    current_user = await get_optional_user(request, session)
    user_msg = req.message.strip()
    user_msg_lower = user_msg.lower()
    
    # Allow anonymous access since MSME does not require login anymore
    if not current_user:
        current_user = User(email="anonymous@guest.com", full_name="Guest User")
    
    # Check if a chat session exists
    result = await session.execute(select(ChatSession).where(ChatSession.user_email == current_user.email))
    chat_state = result.scalars().first()
    
    if not chat_state:
        chat_state = ChatSession(user_email=current_user.email, current_state="IDLE")
        session.add(chat_state)
        await session.commit()
        await session.refresh(chat_state)
        
    state = chat_state.current_state
    
    # Handle Reset Escape Hatch
    if "restart msme" in user_msg_lower or "cancel" in user_msg_lower or ("generate automation" in user_msg_lower and "msme" in user_msg_lower):
        chat_state.current_state = "IDLE"
        session.add(chat_state)
        await session.commit()
        state = "IDLE"
        if not ("generate automation" in user_msg_lower):
            return {"reply": "State reset. How else can I assist you today?"}

    # Trigger MSME flow from IDLE for any generic greeting or MSME request
    if state == "IDLE":
        # Create or Get MSME Registration
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        if not reg:
            reg = MSMERegistration(user_email=current_user.email)
            session.add(reg)
            
        chat_state.current_state = "ASK_AADHAR"
        session.add(chat_state)
        await session.commit()
        
        return {"reply": f"Hello! I am your AI Assistant standing by for the MSME Udyam Registration automation. 🤖\n\nTo securely connect to the government portal and autofill your form, I need exactly two things from you.\n\n**First, please enter your 12-digit Aadhar Number.**"}
        
    # State: ASK_AADHAR
    if state == "ASK_AADHAR":
        import re
        digits = re.sub(r'\D', '', user_msg)
        if len(digits) == 12:
            reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
            reg = reg_result.scalars().first()
            reg.aadhar_number = digits
            session.add(reg)
            
            chat_state.current_state = "ASK_NAME"
            session.add(chat_state)
            await session.commit()
            return {"reply": "Securely saved.\n\n**Next, please provide your exact Name as printed on the Aadhar Card.**"}
        else:
            return {"reply": "That doesn't look like a standard 12-digit Aadhar number. Please try again or type 'cancel'."}

    # State: ASK_NAME
    if state == "ASK_NAME":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.name_as_per_aadhar = user_msg # Original casing
        session.add(reg)
        
        chat_state.current_state = "ASK_ORG_TYPE"
        session.add(chat_state)
        await session.commit()
        
        return {"reply": f"Name verified!\n\n**Next, please type your Organization Type (e.g. Proprietary, Partnership, Hindu Undivided Family, Company):**"}

    # State: ASK_ORG_TYPE
    if state == "ASK_ORG_TYPE":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.organisation_type = user_msg
        session.add(reg)
        
        chat_state.current_state = "ASK_PAN"
        session.add(chat_state)
        await session.commit()
        
        return {"reply": f"Got it.\n\n**Now, please enter your PAN Number.**"}

    # State: ASK_PAN
    if state == "ASK_PAN":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.pan_number = user_msg
        session.add(reg)
        
        chat_state.current_state = "ASK_PAN_NAME"
        session.add(chat_state)
        await session.commit()
        
        return {"reply": f"Saved.\n\n**Please enter the Name exactly as printed on the PAN Card.**"}

    # State: ASK_PAN_NAME
    if state == "ASK_PAN_NAME":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.pan_name = user_msg
        session.add(reg)
        
        chat_state.current_state = "ASK_PAN_DOB"
        session.add(chat_state)
        await session.commit()
        
        return {"reply": f"Saved.\n\n**Finally, please enter the Date of Birth or Incorporation Date as per PAN (DD/MM/YYYY).**"}

    # State: ASK_PAN_DOB
    if state == "ASK_PAN_DOB":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.pan_dob = user_msg
        session.add(reg)
        
        chat_state.current_state = "ASK_MOBILE"
        session.add(chat_state)
        await session.commit()
        
        return {"reply": f"Great. Now, let's collect the additional details required by the Udyam portal.\n\n**Please enter your Mobile Number.**"}

    # Phase 2 States:
    # State: ASK_MOBILE
    if state == "ASK_MOBILE":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.mobile_number = user_msg
        session.add(reg)
        
        chat_state.current_state = "ASK_EMAIL"
        session.add(chat_state)
        await session.commit()
        return {"reply": f"**Please enter your Email Address.**"}

    # State: ASK_EMAIL
    if state == "ASK_EMAIL":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.email = user_msg
        session.add(reg)
        
        chat_state.current_state = "ASK_SOCIAL_CATEGORY"
        session.add(chat_state)
        await session.commit()
        return {"reply": f"**What is your Social Category?** (Reply with one: General, SC, ST, OBC)"}

    # State: ASK_SOCIAL_CATEGORY
    if state == "ASK_SOCIAL_CATEGORY":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.social_category = user_msg
        session.add(reg)
        
        chat_state.current_state = "ASK_GENDER"
        session.add(chat_state)
        await session.commit()
        return {"reply": f"**What is your Gender?** (Reply with one: Male, Female, Others)"}

    # State: ASK_GENDER
    if state == "ASK_GENDER":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.gender = user_msg
        session.add(reg)
        
        chat_state.current_state = "ASK_SPECIALLY_ABLED"
        session.add(chat_state)
        await session.commit()
        return {"reply": f"**Are you Specially Abled (DIVYANG)?** (Reply: Yes or No)"}

    # State: ASK_SPECIALLY_ABLED
    if state == "ASK_SPECIALLY_ABLED":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.specially_abled = user_msg
        session.add(reg)
        
        chat_state.current_state = "ASK_ENTERPRISE_NAME"
        session.add(chat_state)
        await session.commit()
        return {"reply": f"**What is the Name of your Enterprise?**"}

    # State: ASK_ENTERPRISE_NAME
    if state == "ASK_ENTERPRISE_NAME":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.enterprise_name = user_msg
        session.add(reg)
        
        chat_state.current_state = "ASK_PLANT_NAME"
        session.add(chat_state)
        await session.commit()
        return {"reply": f"**What is the Plant/Unit Name?**"}

    # State: ASK_PLANT_NAME
    if state == "ASK_PLANT_NAME":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.plant_name = user_msg
        session.add(reg)
        
        chat_state.current_state = "ASK_PLANT_ADDRESS"
        session.add(chat_state)
        await session.commit()
        return {"reply": f"**Please provide the Location of Plant/Unit.**\nProvide exactly in this comma-separated format:\n`Flat/Door/Block, Name of Premises/Building, Village/Town, Block, Road/Street, City, Pin, State, District`"}

    # State: ASK_PLANT_ADDRESS
    if state == "ASK_PLANT_ADDRESS":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.plant_address = user_msg
        session.add(reg)
        
        chat_state.current_state = "ASK_OFFICIAL_ADDRESS"
        session.add(chat_state)
        await session.commit()
        return {"reply": f"**Please provide the Official Address of Enterprise.**\nProvide exactly in this comma-separated format:\n`Flat/Door/Block, Name of Premises/Building, Village/Town, Block, Road/Street, City, Pin, State, District`"}

    # State: ASK_OFFICIAL_ADDRESS
    if state == "ASK_OFFICIAL_ADDRESS":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.official_address = user_msg
        session.add(reg)
        
        chat_state.current_state = "ASK_PREV_REGISTRATION"
        session.add(chat_state)
        await session.commit()
        return {"reply": f"**Previous EM-II/UAM Registration Number, if any?** (Reply: N/A, EM-II, or Previous UAM)"}

    # State: ASK_PREV_REGISTRATION
    if state == "ASK_PREV_REGISTRATION":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.previous_registration = user_msg
        session.add(reg)
        
        chat_state.current_state = "ASK_STATUS_ENTERPRISE"
        session.add(chat_state)
        await session.commit()
        return {"reply": f"**Status of Enterprise:** Provide Date of Incorporation (DD/MM/YYYY), Whether business commenced (Yes/No), and Date of commencement (DD/MM/YYYY) separated by commas.\nExample: `01/01/2020, Yes, 01/01/2020`"}

    # State: ASK_STATUS_ENTERPRISE
    if state == "ASK_STATUS_ENTERPRISE":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        
        parts = [p.strip() for p in user_msg.split(',')]
        if len(parts) >= 3:
            reg.date_of_incorporation = parts[0]
            reg.business_commenced = parts[1]
            reg.date_of_commencement = parts[2]
        else:
            # Simple fallback
            reg.date_of_incorporation = parts[0] if len(parts) > 0 else "01/01/2000"
            reg.business_commenced = "Yes"
            reg.date_of_commencement = "01/01/2000"

        session.add(reg)
        
        chat_state.current_state = "ASK_BANK_DETAILS"
        session.add(chat_state)
        await session.commit()
        return {"reply": f"**Please provide your Bank Details.**\nProvide exactly in this comma-separated format:\n`Bank Name, IFSC Code, Account Number`\nExample: `State Bank of India, SBIN0001234, 123456789`"}

    # Phase 3 States:
    # State: ASK_BANK_DETAILS
    if state == "ASK_BANK_DETAILS":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        
        parts = [p.strip() for p in user_msg.split(',')]
        reg.bank_name = parts[0] if len(parts) > 0 else "Unknown Bank"
        reg.ifsc_code = parts[1] if len(parts) > 1 else ""
        reg.bank_account_number = parts[2] if len(parts) > 2 else ""
        session.add(reg)
        
        chat_state.current_state = "ASK_MAJOR_ACTIVITY"
        session.add(chat_state)
        await session.commit()
        return {"reply": f"**What is the Major Activity of the Unit?**\n(Reply with one: `Manufacturing` or `Services`)"}

    # State: ASK_MAJOR_ACTIVITY
    if state == "ASK_MAJOR_ACTIVITY":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.major_activity = user_msg
        session.add(reg)
        
        if "service" in user_msg.lower():
            chat_state.current_state = "ASK_MAJOR_ACTIVITY_UNDER_SERVICES"
            session.add(chat_state)
            await session.commit()
            return {"reply": f"**Major Activity Under Services:**\n(Reply with one: `Non-Trading` or `Trading`)"}
        else:
            chat_state.current_state = "ASK_NIC_ACTIVITY_TYPE"
            session.add(chat_state)
            await session.commit()
            return {"reply": f"**For the NIC Code, what is the Activity Type?**\n(Reply with one: `Manufacturing`, `Services`, or `Trading`)"}

    # State: ASK_MAJOR_ACTIVITY_UNDER_SERVICES
    if state == "ASK_MAJOR_ACTIVITY_UNDER_SERVICES":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.major_activity_under_services = user_msg
        session.add(reg)
        
        chat_state.current_state = "ASK_NIC_ACTIVITY_TYPE"
        session.add(chat_state)
        await session.commit()
        return {"reply": f"**For the NIC Code, what is the Activity Type?**\n(Reply with one: `Manufacturing`, `Services`, or `Trading`)"}

    # State: ASK_NIC_ACTIVITY_TYPE
    if state == "ASK_NIC_ACTIVITY_TYPE":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        activity = user_msg.strip().lower()
        
        # Normalize activity
        if "manufactur" in activity:
            activity = "manufacturing"
        elif "service" in activity:
            activity = "services"
        elif "trading" in activity:
            activity = "trading"
        else:
            return {"reply": "Please choose one: `Manufacturing`, `Services`, or `Trading`."}

        reg.nic_activity_type = activity.capitalize()
        session.add(reg)
        
        chat_state.current_state = "ASK_NIC_2_DIGIT"
        session.add(chat_state)
        await session.commit()
        
        # Get NIC 2 options for this activity
        options = NIC_DATA.get(activity, {})
        reply_msg = f"Got it. **For {activity.capitalize()}, please choose your NIC 2-Digit Code.**\n\n"
        
        if options:
            for code, data in options.items():
                reply_msg += f"`{code}` - {data.get('description')}\n"
            reply_msg += "\n*Please type the 2-digit code.*"
        else:
            reply_msg += "I'm still loading the specific codes for this category. Please type your 2-digit code manually for now."
            
        return {"reply": reply_msg}
        
    # State: ASK_NIC_2_DIGIT
    if state == "ASK_NIC_2_DIGIT":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        
        # Robust parsing: extract leading digits
        import re
        match = re.search(r'^(\d+)', user_msg.strip())
        nic2_code = match.group(1) if match else user_msg.strip()
        
        reg.nic_2_digit = nic2_code
        session.add(reg)
        
        chat_state.current_state = "ASK_NIC_4_DIGIT"
        session.add(chat_state)
        await session.commit()
        
        activity = reg.nic_activity_type.lower()
        nic2_data = NIC_DATA.get(activity, {}).get(nic2_code, {})
        nic4_options = nic2_data.get("nic4", {})

        reply_msg = f"**NIC 2-Digit: {nic2_code} ({nic2_data.get('description', 'Unknown')})**\n\n"
        reply_msg += "Please provide your **NIC 4-Digit Code**.\n\n"
        
        if nic4_options:
            reply_msg += "Here are the options based on your selection:\n"
            for code, data in nic4_options.items():
                reply_msg += f"- `{code}`: {data.get('description')}\n"
        else:
            reply_msg += "*(Note: The MSME portal loads these dynamically. Please enter the valid 4-digit code and the automation will select it!)*"
            
        return {"reply": reply_msg}
        
    # State: ASK_NIC_4_DIGIT
    if state == "ASK_NIC_4_DIGIT":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        
        # Robust parsing: extract leading digits
        import re
        match = re.search(r'^(\d+)', user_msg.strip())
        nic4_code = match.group(1) if match else user_msg.strip()
        
        reg.nic_4_digit = nic4_code
        session.add(reg)
        
        chat_state.current_state = "ASK_NIC_5_DIGIT"
        session.add(chat_state)
        await session.commit()
        
        activity = reg.nic_activity_type.lower()
        nic2_code = reg.nic_2_digit
        nic4_data = NIC_DATA.get(activity, {}).get(nic2_code, {}).get("nic4", {}).get(nic4_code, {})
        nic5_options = nic4_data.get("nic5", {})

        reply_msg = f"**NIC 4-Digit: {nic4_code} ({nic4_data.get('description', 'Unknown')})**\n\n"
        reply_msg += f"Please provide your **NIC 5-Digit Code**.\n\n"
        
        if nic5_options:
            reply_msg += "Here are the options based on your selection:\n"
            for code, desc in nic5_options.items():
                reply_msg += f"- `{code}`: {desc}\n"
        else:
            reply_msg += "*(Please enter your valid 5-Digit code below and the Udyam Automation will automatically select it!)*"
        
        return {"reply": reply_msg}
        
    # State: ASK_NIC_5_DIGIT
    if state == "ASK_NIC_5_DIGIT":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        
        # Robust parsing: extract leading digits
        import re
        match = re.search(r'^(\d+)', user_msg.strip())
        nic5_code = match.group(1) if match else user_msg.strip()
        
        reg.nic_5_digit = nic5_code
        session.add(reg)
        
        chat_state.current_state = "ASK_PERSONS_EMPLOYED"
        session.add(chat_state)
        await session.commit()
        return {"reply": f"**NIC 5-Digit: {reg.nic_5_digit} saved.**\n\n**Number of persons employed?**\nProvide numeric counts in this comma-separated format:\n`Male, Female, Others`\nExample: `10, 5, 0`"}
        

    # State: ASK_PERSONS_EMPLOYED
    if state == "ASK_PERSONS_EMPLOYED":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        
        parts = [p.strip() for p in user_msg.split(',')]
        reg.persons_employed_male = parts[0] if len(parts) > 0 else "0"
        reg.persons_employed_female = parts[1] if len(parts) > 1 else "0"
        reg.persons_employed_others = parts[2] if len(parts) > 2 else "0"
        session.add(reg)
        
        chat_state.current_state = "ASK_ITR_GSTIN"
        session.add(chat_state)
        await session.commit()
        return {"reply": f"**Final Question:** Have you filed ITR for Previous Year (Yes/No)? And Do you have GSTIN (Yes/No/Exempted)?\nReply separated by comma, e.g., `Yes, No`"}

    # State: ASK_ITR_GSTIN
    if state == "ASK_ITR_GSTIN":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        
        parts = [p.strip() for p in user_msg.split(',')]
        reg.itr_filed = parts[0] if len(parts) > 0 else "No"
        reg.has_gstin = parts[1] if len(parts) > 1 else "No"
        
        session.add(reg)
        
        chat_state.current_state = "ASK_OTP"
        session.add(chat_state)
        await session.commit()
        
        # TRIGGER THE BACKGROUND AUTOMATION SCRIPT
        from app.services.msme_automation import run_msme_automation
        asyncio.create_task(run_msme_automation(reg.id))
        
        return {"reply": f"All details collected securely! 🚀\n\n**Launching the Government Portal Connection now...**\n\nThe automation is connecting to the Udyam portal. Please wait up to 60 seconds. **When you receive the 6-digit Aadhar OTP on your linked mobile number, please type it here.**"}        
    # State: ASK_OTP
    if state == "ASK_OTP":
        import re
        digits = re.sub(r'\D', '', user_msg)
        if len(digits) == 6:
            reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
            reg = reg_result.scalars().first()
            reg.otp_code = digits
            session.add(reg)
            
            chat_state.current_state = "READY"
            session.add(chat_state)
            await session.commit()
            
            return {"reply": "OTP received! Injecting it into the active automation session now... Please hold on while we complete the validation."}
        else:
            return {"reply": "That doesn't look like a standard 6-digit OTP. Please try again or type 'cancel'."}
            
    # State: READY / AUTOMATING
    if state == "READY":
        return {"reply": "The MSME Automation has been triggered. If you wish to restart the collection phase, please say 'restart msme'."}

    # Generic Fallback
    return {"reply": "I am standing by for MSME automation. Please type 'restart msme' to begin."}

