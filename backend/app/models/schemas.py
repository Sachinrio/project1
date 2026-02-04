from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

# --- NEW: Ticket Class Model ---
class TicketClass(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id", index=True)
    type: str = "paid"  # free, paid, donation
    name: str
    price: float = 0.0
    quantity: int  # Total allocated quantity
    quantity_sold: int = Field(default=0)  # Track sales
    min_quantity: int = 1
    max_quantity: int = 10
    sales_start: Optional[datetime] = None
    sales_end: Optional[datetime] = None
    description: Optional[str] = None
    is_active: bool = True
    currency: str = "INR"  # Default currency

class TicketClassCreate(SQLModel):
    name: str
    type: str = "paid"
    price: float = 0.0
    quantity: int
    description: Optional[str] = None
    sales_start: Optional[datetime] = None
    sales_end: Optional[datetime] = None
    min_quantity: int = 1
    max_quantity: int = 10

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Unique ID from Eventbrite to prevent duplicates
    eventbrite_id: str = Field(unique=True, index=True) 
    
    # Core fields for fast filtering/sorting
    title: str
    description: Optional[str] = None
    start_time: datetime 
    end_time: Optional[datetime] = None
    
    url: str
    image_url: Optional[str] = None
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None
    organizer_name: Optional[str] = None
    is_free: bool = Field(default=True)
    online_event: bool = Field(default=False)
    category: Optional[str] = Field(default="Business", index=True)
    
    # New Fields
    capacity: Optional[int] = None
    registration_deadline: Optional[datetime] = None
    meeting_link: Optional[str] = None
    meeting_link_private: bool = Field(default=True)
    timezone: Optional[str] = "UTC"
    
    # --- NEW: The JSON Dump Column ---
    # This uses PostgreSQL's JSONB type for efficient storage
    raw_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    
    created_at: datetime = Field(default_factory=datetime.now)

class EventCreate(SQLModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = "Business"
    is_free: bool = True
    online_event: bool = False
    
    # New Fields
    capacity: Optional[int] = None
    registration_deadline: Optional[datetime] = None
    meeting_link: Optional[str] = None
    meeting_link_private: bool = True
    timezone: Optional[str] = "UTC"
    
    # Pro Fields
    organizer_name: Optional[str] = None
    organizer_email: Optional[str] = None
    price: Optional[str] = None
    
    # Content Fields
    agenda: Optional[List[Dict[str, Any]]] = None
    speakers: Optional[List[Dict[str, Any]]] = None
    gallery_images: Optional[List[str]] = None

    # --- NEW: Ticket List for Creation ---
    tickets: Optional[List[TicketClassCreate]] = None

class UserRegistration(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id")
    user_email: str
    registered_at: datetime = Field(default_factory=datetime.now)

    # Relationship to Event
    event: Optional[Event] = Relationship()

    # Auto-Registration Fields
    confirmation_id: Optional[str] = None
    status: str = Field(default="PENDING") # PENDING, SUCCESS, FAILED
    
    # --- NEW: Ticket Link ---
    ticket_class_id: Optional[int] = Field(default=None, foreign_key="ticketclass.id")

    # Store checkout details (attendee info, ticket breakdown)
    raw_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))

    # Check-in Status
    checked_in_at: Optional[datetime] = None

# --- User Authentication Models ---

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)
    razorpay_account_id: Optional[str] = None # Linked Account ID for Payouts

    # Profile fields
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None  # For storing image URL or path

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    
    # Forgot Password Fields
    reset_otp: Optional[str] = None
    otp_expires_at: Optional[datetime] = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    email: Optional[str] = None

class GoogleToken(SQLModel):
    token: str

class EventListResponse(SQLModel):
    data: List[Event]
    total: int
    page: int
    limit: int

# --- Following System Models ---

class Follow(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    follower_email: str = Field(index=True)  # The user who is following
    followed_email: str = Field(index=True)  # The user being followed
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    follower: Optional["User"] = Relationship(sa_relationship_kwargs={"foreign_keys": "Follow.follower_email", "primaryjoin": "Follow.follower_email == User.email"})
    followed: Optional["User"] = Relationship(sa_relationship_kwargs={"foreign_keys": "Follow.followed_email", "primaryjoin": "Follow.followed_email == User.email"})
