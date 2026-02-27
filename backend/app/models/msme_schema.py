from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class MSMERegistrationBase(SQLModel):
    user_email: str = Field(index=True)
    aadhar_number: Optional[str] = None
    name_as_per_aadhar: Optional[str] = None
    pan_number: Optional[str] = None
    pan_name: Optional[str] = None
    pan_dob: Optional[str] = None
    organisation_type: Optional[str] = None
    business_name: Optional[str] = None
    
    # Phase 2 Fields
    itr_filed: Optional[str] = None
    has_gstin: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[str] = None
    social_category: Optional[str] = None
    gender: Optional[str] = None
    specially_abled: Optional[str] = None
    enterprise_name: Optional[str] = None
    plant_name: Optional[str] = None
    plant_address: Optional[str] = None # Consolidated for UX
    official_address: Optional[str] = None # Consolidated for UX
    previous_registration: Optional[str] = None
    date_of_incorporation: Optional[str] = None
    business_commenced: Optional[str] = None
    date_of_commencement: Optional[str] = None

    otp_code: Optional[str] = None
    status: str = Field(default="IN_PROGRESS") # IN_PROGRESS, AUTOMATING, COMPLETED, FAILED
class MSMERegistration(MSMERegistrationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_email: str = Field(index=True)
    current_state: str = Field(default="IDLE") # IDLE, ASK_AADHAR, ASK_NAME, ASK_PAN, READY
    last_updated: datetime = Field(default_factory=datetime.utcnow)
