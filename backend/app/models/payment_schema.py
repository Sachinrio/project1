from pydantic import BaseModel
from typing import Optional

class OrderCreate(BaseModel):
    amount: int  # Amount in Rupees
    currency: str = "INR"
    event_id: Optional[int] = None # To identify the organizer

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class PayoutDetails(BaseModel):
    account_holder_name: str
    account_number: str
    ifsc_code: str
    mobile_number: str
