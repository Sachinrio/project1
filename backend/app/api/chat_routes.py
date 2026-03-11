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
        reg.nic_activity_type = user_msg.strip()
        session.add(reg)
        
        chat_state.current_state = "ASK_NIC_2_DIGIT"
        session.add(chat_state)
        await session.commit()
        
        reply_msg = "**Please provide your NIC 2-Digit Code.**\n\n"
        if "manufactur" in user_msg.lower():
            reply_msg += (
                "Here are the Manufacturing 2-Digit options as reference:\n"
                "`01` - Crop/Animal Production\n`05` - Mining/Quarrying\n`06` - Extraction of crude petroleum/natural gas\n"
                "`07` - Mining metal ores\n`08` - Other mining/quarrying\n`09` - Mining support tech\n"
                "`10` - Food products\n`11` - Beverages\n`12` - Tobacco\n`13` - Textiles\n"
                "`14` - Wearing apparel\n`15` - Leather products\n`16` - Wood products\n`17` - Paper products\n"
                "`18` - Printing/recording\n`19` - Petroleum products\n`20` - Chemical products\n`21` - Pharmaceuticals\n"
                "`22` - Rubber/plastics\n`23` - Non-metallic minerals\n`24` - Basic metals\n`25` - Fabricated metals\n"
                "`26` - Computer/electronic/optical\n`27` - Electrical equipment\n`28` - Machinery/equipment\n"
                "`29` - Motor vehicles\n`30` - Other transport equipment\n`31` - Furniture\n`32` - Other manufacturing\n"
                "`33` - Repair/installation of machinery\n`35` - Electricity, gas, steam\n`36` - Water collection\n"
                "`37` - Sewerage\n`38` - Waste collection\n`39` - Remediation activities\n`41` - Construction of building\n"
                "`42` - Civil Engineering\n`43` - Specialized construction\n\n"
            )
        elif "service" in user_msg.lower():
            reply_msg += (
                "Here are the Services 2-Digit options as reference:\n"
                "`49` - Land transport/pipelines\n`50` - Water transport\n`51` - Air Transport\n`52` - Warehousing and support activities\n"
                "`53` - Postal and courier activities\n`55` - Accommodation\n`56` - Food and beverage service activities\n"
                "`58` - Publishing activities\n`59` - Motion picture/music activities\n`60` - Broadcasting and programming\n"
                "`61` - Telecommunications\n`62` - Computer programming/consultancy\n`63` - Information service activities\n"
                "`64` - Financial service activities\n`65` - Insurance and pension funding\n`66` - Other financial activities\n"
                "`68` - Real estate activities\n`69` - Legal and accounting activities\n`70` - Head offices/management consultancy\n"
                "`71` - Architecture/engineering/technical testing\n`72` - Scientific research and development\n`73` - Advertising and market research\n"
                "`74` - Other professional/scientific activities\n`75` - Veterinary activities\n`77` - Rental and leasing activities\n"
                "`78` - Employment activities\n`79` - Travel agency/tours\n`80` - Security and investigation\n`81` - Services to buildings and landscape\n"
                "`82` - Office administrative/support\n`84` - Public administration and defence\n`85` - Education\n`86` - Human health activities\n"
                "`87` - Residential care activities\n`88` - Social work activities without accommodation\n`90` - Creative, arts and entertainment\n"
                "`91` - Libraries, archives, museums\n`93` - Sports, amusement and recreation\n`94` - Activities of membership organizations\n"
                "`95` - Repair of computers/personal goods\n`96` - Other personal service activities\n\n"
            )
        elif "trading" in user_msg.lower():
            reply_msg += (
                "Here are the Trading 2-Digit options as reference:\n"
                "`45` - Wholesale and retail trade and repair of motor vehicles and motorcycles\n"
                "`46` - Wholesale trade, except of motor vehicles and motorcycles\n"
                "`47` - Retail trade, except of motor vehicles and motorcycles\n\n"
            )
            
        reply_msg += "Please enter the **2-Digit Code block** (e.g. `10` for Food Products or `62` for Computer programming)."
            
        return {"reply": reply_msg}
        
    # State: ASK_NIC_2_DIGIT
    if state == "ASK_NIC_2_DIGIT":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.nic_2_digit = user_msg.strip()
        session.add(reg)
        
        chat_state.current_state = "ASK_NIC_4_DIGIT"
        session.add(chat_state)
        await session.commit()
        
        reply_msg = f"**Please provide your NIC 4-Digit Code.**\n\n"
        reply_msg += "*(Note: The MSME portal loads these dynamically based on your 2-Digit choice. Because there are over 1,000 combinations, we cannot list them all here. But the automation WILL select whatever valid code you enter!)*\n\n"
        
        if "01" in user_msg:
            reply_msg += "For example, for `01`, the options include:\n- `0146` - Raising of poultry\n- `0149` - Raising of other animals\n- `0161` - Support activities for crop production\n- `0162` - Support activities for animal production\n- `0163` - Post-harvest crop activities\n- `0164` - Seed processing for propagation\n\n"
        elif "05" in user_msg:
            reply_msg += "For `05`, the options include:\n- `0510` - Mining of hard coal\n- `0520` - Mining of lignite\n\n"
        elif "06" in user_msg:
            reply_msg += "For `06`, the options include:\n- `0610` - Extraction of crude petroleum\n- `0620` - Extraction of natural gas\n\n"
        elif "07" in user_msg:
            reply_msg += "For `07`, the options include:\n- `0710` - Mining of iron ores\n- `0721` - Mining of uranium and thorium ores\n- `0729` - Mining of other non-ferrous metal ores\n\n"
        elif "08" in user_msg:
            reply_msg += "For `08`, the options include:\n- `0810` - Quarrying of stone, sand and clay\n- `0891` - Mining of chemical and fertilizer minerals\n- `0892` - Extraction and agglomeration of peat\n- `0893` - Extraction of salt\n- `0899` - Other mining and quarrying n.e.c.\n\n"
        elif "09" in user_msg:
            reply_msg += "For `09`, the options include:\n- `0910` - Support activities for petroleum and natural gas mining\n- `0990` - Support activities for other mining and quarrying\n\n"
        elif "10" in user_msg:
            reply_msg += "For `10`, the options include:\n- `1010` - Processing and preserving of meat\n- `1020` - Processing and preserving of fish, crustaceans and molluscs and products thereof\n- `1030` - Processing and preserving of fruit and vegetables\n- `1040` - Manufacture of vegetable and animal oils and fats\n- `1050` - Manufacture of dairy products\n- `1061` - Manufacture of grain mill products\n- `1062` - Manufacture of starches and starch products\n- `1071` - Manufacture of bakery products\n- `1072` - Manufacture of sugar\n- `1073` - Manufacture of cocoa, chocolate and sugar confectionery\n- `1074` - Manufacture of macaroni, noodles, couscous and similar farinaceous products\n- `1075` - Manufacture of prepared meals and dishes\n- `1079` - Manufacture of other food products n.e.c.\n- `1080` - Manufacture of prepared animal feeds\n\n"
        elif "11" in user_msg:
            reply_msg += "For `11`, the options include:\n- `1101` - Distilling, rectifying and blending of spirits; ethyl alcohol production from fermented materials\n- `1102` - Manufacture of wines\n- `1103` - Manufacture of malt liquors and malt\n- `1104` - Manufacture of soft drinks; production of mineral waters and other bottled waters\n\n"
        elif "12" in user_msg:
            reply_msg += "For `12`, the options include:\n- `1200` - Manufacture of tobacco products\n\n"
        elif "13" in user_msg:
            reply_msg += "For `13`, the options include:\n- `1311` - Preparation and spinning of textile fibres\n- `1312` - Weaving of textiles\n- `1313` - Finishing of textiles\n- `1391` - Manufacture of knitted and crocheted fabrics\n- `1392` - Manufacture of made-up textile articles, except apparel\n- `1393` - Manufacture of carpets and rugs\n- `1394` - Manufacture of cordage, rope, twine and netting\n- `1399` - Manufacture of other textiles n.e.c.\n\n"
        elif "14" in user_msg:
            reply_msg += "For `14`, the options include:\n- `1410` - Manufacture of wearing apparel, except fur apparel\n- `1420` - Manufacture of articles of fur\n- `1430` - Manufacture of knitted and crocheted apparel\n\n"
        elif "15" in user_msg:
            reply_msg += "For `15`, the options include:\n- `1511` - Tanning and dressing of leather; manufacture of luggage, handbags, saddlery and harness\n- `1512` - Manufacture of footwear\n- `1520` - Manufacture of footwear\n\n"
        elif "16" in user_msg:
            reply_msg += "For `16`, the options include:\n- `1610` - Saw milling and planing of wood\n- `1621` - Manufacture of veneer sheets and wood-based panels\n- `1622` - Manufacture of builders' carpentry and joinery\n- `1623` - Manufacture of wooden containers\n- `1629` - Manufacture of other products of wood; manufacture of articles of cork, straw and plaiting materials\n\n"
        elif "17" in user_msg:
            reply_msg += "For `17`, the options include:\n- `1701` - Manufacture of pulp, paper and paperboard\n- `1702` - Manufacture of corrugated paper and paperboard and containers of paper and paperboard\n- `1709` - Manufacture of other articles of paper and paperboard\n\n"
        elif "18" in user_msg:
            reply_msg += "For `18`, the options include:\n- `1811` - Printing\n- `1812` - Service activities related to printing\n- `1820` - Reproduction of recorded media\n\n"
        elif "19" in user_msg:
            reply_msg += "For `19`, the options include:\n- `1910` - Manufacture of coke oven products\n- `1920` - Manufacture of refined petroleum products\n\n"
        elif "20" in user_msg:
            reply_msg += "For `20`, the options include:\n- `2011` - Manufacture of basic chemicals\n- `2012` - Manufacture of fertilizers and nitrogen compounds\n- `2013` - Manufacture of plastics and synthetic rubber in primary forms\n- `2021` - Manufacture of pesticides and other agrochemical products\n- `2022` - Manufacture of paints, varnishes and similar coatings, printing ink and mastics\n- `2023` - Manufacture of soap and detergents, cleaning and polishing preparations, perfumes and toilet preparations\n- `2029` - Manufacture of other chemical products n.e.c.\n- `2030` - Manufacture of man-made fibres\n\n"
        elif "21" in user_msg:
            reply_msg += "For `21`, the options include:\n- `2100` - Manufacture of pharmaceuticals, medicinal chemical and botanical products\n\n"
        elif "22" in user_msg:
            reply_msg += "For `22`, the options include:\n- `2211` - Manufacture of rubber tyres and tubes; retreading and rebuilding of rubber tyres\n- `2219` - Manufacture of other rubber products\n- `2220` - Manufacture of plastics products\n\n"
        elif "23" in user_msg:
            reply_msg += "For `23`, the options include:\n- `2310` - Manufacture of glass and glass products\n- `2391` - Manufacture of refractory products\n- `2392` - Manufacture of clay building materials\n- `2393` - Manufacture of other porcelain and ceramic products\n- `2394` - Manufacture of cement, lime and plaster\n- `2395` - Manufacture of articles of concrete, cement and plaster\n- `2396` - Cutting, shaping and finishing of stone\n- `2399` - Manufacture of other non-metallic mineral products n.e.c.\n\n"
        elif "24" in user_msg:
            reply_msg += "For `24`, the options include:\n- `2410` - Manufacture of basic iron and steel\n- `2420` - Manufacture of basic precious and other non-ferrous metals\n- `2431` - Casting of iron and steel\n- `2432` - Casting of non-ferrous metals\n\n"
        elif "25" in user_msg:
            reply_msg += "For `25`, the options include:\n- `2511` - Manufacture of structural metal products\n- `2512` - Manufacture of tanks, reservoirs and containers of metal\n- `2513` - Manufacture of steam generators, except central heating hot water boilers\n- `2520` - Manufacture of weapons and ammunition\n- `2591` - Forging, pressing, stamping and roll-forming of metal; powder metallurgy\n- `2592` - Treatment and coating of metals; machining\n- `2593` - Manufacture of cutlery, hand tools and general hardware\n- `2599` - Manufacture of other fabricated metal products n.e.c.\n\n"
        elif "26" in user_msg:
            reply_msg += "For `26`, the options include:\n- `2610` - Manufacture of electronic components and boards\n- `2620` - Manufacture of computers and peripheral equipment\n- `2630` - Manufacture of communication equipment\n- `2640` - Manufacture of consumer electronics\n- `2651` - Manufacture of measuring, testing, navigating and control equipment\n- `2652` - Manufacture of watches and clocks\n- `2660` - Manufacture of irradiation, electromedical and electrotherapeutic equipment\n- `2670` - Manufacture of optical instruments and photographic equipment\n- `2680` - Manufacture of magnetic and optical media\n\n"
        elif "27" in user_msg:
            reply_msg += "For `27`, the options include:\n- `2710` - Manufacture of electric motors, generators, transformers and electricity distribution and control apparatus\n- `2720` - Manufacture of batteries and accumulators\n- `2731` - Manufacture of fibre optic cables for data transmission or live transmission of images\n- `2732` - Manufacture of other electronic and electric wires and cables\n- `2733` - Manufacture of wiring devices\n- `2740` - Manufacture of electric lighting equipment\n- `2750` - Manufacture of domestic appliances\n- `2790` - Manufacture of other electrical equipment\n\n"
        elif "28" in user_msg:
            reply_msg += "For `28`, the options include:\n- `2811` - Manufacture of engines and turbines, except aircraft, vehicle and cycle engines\n- `2812` - Manufacture of fluid power equipment\n- `2813` - Manufacture of other pumps, compressors, taps and valves\n- `2814` - Manufacture of bearings, gears, gearing and driving elements\n- `2815` - Manufacture of ovens, furnaces and furnace burners\n- `2816` - Manufacture of lifting and handling equipment\n- `2817` - Manufacture of office machinery and equipment\n- `2818` - Manufacture of power-driven hand tools\n- `2819` - Manufacture of other general-purpose machinery\n- `2821` - Manufacture of agricultural and forestry machinery\n- `2822` - Manufacture of metal-forming machinery and machine tools\n- `2823` - Manufacture of machinery for metallurgy\n- `2824` - Manufacture of machinery for mining, quarrying and construction\n- `2825` - Manufacture of machinery for food, beverage and tobacco processing\n- `2826` - Manufacture of machinery for textile, apparel and leather production\n- `2829` - Manufacture of other special-purpose machinery\n\n"
        elif "29" in user_msg:
            reply_msg += "For `29`, the options include:\n- `2910` - Manufacture of motor vehicles\n- `2920` - Manufacture of bodies (coachwork) for motor vehicles; manufacture of trailers and semi-trailers\n- `2930` - Manufacture of parts and accessories for motor vehicles\n\n"
        elif "30" in user_msg:
            reply_msg += "For `30`, the options include:\n- `3011` - Building of ships and floating structures\n- `3012` - Building of pleasure and sporting boats\n- `3020` - Manufacture of railway locomotives and rolling stock\n- `3030` - Manufacture of air and spacecraft and related machinery\n- `3040` - Manufacture of weapons and ammunition\n- `3091` - Manufacture of motorcycles\n- `3092` - Manufacture of bicycles and invalid carriages\n- `3099` - Manufacture of other transport equipment n.e.c.\n\n"
        elif "31" in user_msg:
            reply_msg += "For `31`, the options include:\n- `3100` - Manufacture of furniture\n\n"
        elif "32" in user_msg:
            reply_msg += "For `32`, the options include:\n- `3211` - Manufacture of jewellery and related articles\n- `3212` - Manufacture of imitation jewellery and related articles\n- `3220` - Manufacture of musical instruments\n- `3230` - Manufacture of sports goods\n- `3240` - Manufacture of games and toys\n- `3250` - Manufacture of medical and dental instruments and supplies\n- `3290` - Other manufacturing n.e.c.\n\n"
        elif "33" in user_msg:
            reply_msg += "For `33`, the options include:\n- `3311` - Repair of fabricated metal products\n- `3312` - Repair of machinery\n- `3313` - Repair of electronic and optical equipment\n- `3314` - Repair of electrical equipment\n- `3315` - Repair of transport equipment, except motor vehicles\n- `3319` - Repair of other equipment\n- `3320` - Installation of industrial machinery and equipment\n\n"
        elif "35" in user_msg:
            reply_msg += "For `35`, the options include:\n- `3510` - Electric power generation, transmission and distribution\n- `3520` - Manufacture of gas; distribution of gaseous fuels through mains\n- `3530` - Steam and air conditioning supply\n\n"
        elif "36" in user_msg:
            reply_msg += "For `36`, the options include:\n- `3600` - Water collection, treatment and supply\n\n"
        elif "37" in user_msg:
            reply_msg += "For `37`, the options include:\n- `3700` - Sewerage\n\n"
        elif "38" in user_msg:
            reply_msg += "For `38`, the options include:\n- `3811` - Collection of non-hazardous waste\n- `3812` - Collection of hazardous waste\n- `3821` - Treatment and disposal of non-hazardous waste\n- `3822` - Treatment and disposal of hazardous waste\n- `3830` - Materials recovery\n\n"
        elif "39" in user_msg:
            reply_msg += "For `39`, the options include:\n- `3900` - Remediation activities and other waste management services\n\n"
        elif "41" in user_msg:
            reply_msg += "For `41`, the options include:\n- `4100` - Construction of buildings\n\n"
        elif "42" in user_msg:
            reply_msg += "For `42`, the options include:\n- `4210` - Construction roads and railways\n- `4220` - Construction of utility projects\n- `4290` - Construction of other civil engineering projects\n\n"
        elif "43" in user_msg:
            reply_msg += "For `43`, the options include:\n- `4311` - Demolition\n- `4312` - Site preparation\n- `4321` - Electrical installation\n- `4322` - Plumbing, heat and air-conditioning installation\n- `4329` - Other construction installation\n- `4330` - Building completion and finishing\n- `4390` - Other specialized construction activities\n\n"
        
        reply_msg += "Please enter your **4-Digit Code** below:"
        return {"reply": reply_msg}
        
    # State: ASK_NIC_4_DIGIT
    if state == "ASK_NIC_4_DIGIT":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.nic_4_digit = user_msg.strip()
        session.add(reg)
        
        chat_state.current_state = "ASK_NIC_5_DIGIT"
        session.add(chat_state)
        await session.commit()
        
        reply_msg = f"**Please provide your NIC 5-Digit Code.**\n\n"
        
        found_options = False
        if "4311" in user_msg:
            reply_msg += "For `4311`, the options include:\n- `43110` - Demolition of buildings and other structures\n\n"
            found_options = True
        elif "4312" in user_msg:
            reply_msg += "For `4312`, the options include:\n- `43121` - Site preparation for mining (overburden removal, mineral site prep)\n- `43122` - Site preparation including drilling, boring, and core sampling\n- `43123` - Clearing of building sites, earth moving, excavation, and landfill\n\n"
            found_options = True
        elif "4321" in user_msg:
            reply_msg += "For `4321`, the options include:\n- `43211` - Installation of electrical wiring and fittings\n- `43212` - Installation of telecommunications, computer network, and cable TV wiring\n- `43219` - Other electrical installation activities n.e.c.\n\n"
            found_options = True
        elif "4322" in user_msg:
            reply_msg += "For `4322`, the options include:\n- `43221` - Installation of plumbing for water, gas, and sanitation equipment\n- `43222` - Installation of heating systems (electric, gas, oil), furnaces, and cooling towers\n\n"
            found_options = True
        elif "4329" in user_msg:
            reply_msg += "For `4329`, the options include:\n- `43291` - Installation of elevators and escalators\n- `43292` - Installation of thermal, sound, or vibration insulation systems\n- `43299` - Other construction installation n.e.c.\n\n"
            found_options = True
        elif "4330" in user_msg:
            reply_msg += "For `4330`, the options include:\n- `43301` - Glazing and installation of glass and windows\n- `43302` - Plastering and woodwork\n- `43303` - Interior and exterior painting, decorating, and floor/wall tiling\n- `43309` - Other building completion and finishing\n\n"
            found_options = True
        elif "4390" in user_msg:
            reply_msg += "For `4390`, the options include:\n- `43900` - Other specialized construction activities (foundation, water proofing, etc.)\n\n"
            found_options = True
            
        if not found_options:
            reply_msg += "*(Similarly, please enter your valid 5-Digit code below and the Udyam Automation will automatically select it from the final dropdown.)*\n\n"
            nic_prefix = "".join(filter(str.isdigit, user_msg))
            if len(nic_prefix) >= 4:
                nic_prefix = nic_prefix[:4]
                reply_msg += f"Example: `{nic_prefix}1` or `{nic_prefix}2`"
            else:
                reply_msg += "Example: `01461` or `10304`"
        else:
            reply_msg += "Please enter your **5-Digit Code** below:"
        
        return {"reply": reply_msg}
        
    # State: ASK_NIC_5_DIGIT
    if state == "ASK_NIC_5_DIGIT":
        reg_result = await session.execute(select(MSMERegistration).where(MSMERegistration.user_email == current_user.email))
        reg = reg_result.scalars().first()
        reg.nic_5_digit = user_msg.strip()
        session.add(reg)
        
        chat_state.current_state = "ASK_PERSONS_EMPLOYED"
        session.add(chat_state)
        await session.commit()
        return {"reply": f"**Number of persons employed?**\nProvide numeric counts in this comma-separated format:\n`Male, Female, Others`\nExample: `10, 5, 0`"}

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

