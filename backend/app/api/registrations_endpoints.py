
# --- 10. MY REGISTRATIONS ENDPOINTS ---

@router.get("/user/registrations")
async def get_user_registrations(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get all events the user has registered for.
    """
    from sqlalchemy.orm import selectinload
    stmt = select(UserRegistration).where(
        UserRegistration.user_email == current_user.email
    ).options(selectinload(UserRegistration.event))
    
    result = await session.execute(stmt)
    registrations = result.scalars().all()
    
    events_list = []
    for reg in registrations:
        if reg.event:
            events_list.append({
                "id": reg.event.id,
                "title": reg.event.title,
                "start_time": reg.event.start_time,
                "end_time": reg.event.end_time,
                "venue_name": reg.event.venue_name,
                "venue_address": reg.event.venue_address,
                "image_url": reg.event.image_url,
                "is_free": reg.event.is_free,
                "online_event": reg.event.online_event,
                "registration_date": reg.registered_at,
                "status": reg.status, # SUCCESS, PENDING, etc.
                "confirmation_id": reg.confirmation_id,
                "ticket_type": (
                    ", ".join([f"{t.get('selectedQty')} x {t.get('name')}" for t in reg.raw_data.get("tickets", []) if t.get("selectedQty", 0) > 0])
                    if reg.raw_data and "tickets" in reg.raw_data else "Standard Entry"
                )
            })
            
    return {"registrations": events_list}

@router.get("/user/registrations/{event_id}/qr")
async def get_registration_qr(
    event_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get QR code for a specific registration.
    """
    stmt = select(UserRegistration).where(
        UserRegistration.event_id == event_id,
        UserRegistration.user_email == current_user.email,
        UserRegistration.status == "SUCCESS"
    ).options(selectinload(UserRegistration.event))
    
    result = await session.execute(stmt)
    registration = result.scalars().first()
    
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
        
    # Generate QR Data
    event = registration.event
    qr_data = f"Ticket ID: {registration.confirmation_id}\nEvent: {event.title}\nUser: {current_user.email}\nValid: {event.start_time}"
    
    # Generate QR Image (using existing utility if available or inline)
    # We imported generate_qr_code from app.core.email_utils earlier
    qr_base64 = generate_qr_code(qr_data)
    
    return {
        "qr_code": qr_base64,
        "event_title": event.title,
        "ticket_id": registration.confirmation_id,
        "payment_id": registration.raw_data.get("payment_id"),
        "amount_paid": registration.raw_data.get("total_amount", 0)
    }

# --- CHECK-IN ENDPOINT ---
from datetime import datetime

class CheckInResponse(SQLModel):
    status: str # SUCCESS, ALREADY_CHECKED_IN, INVALID
    message: str
    attendee: Optional[Dict[str, Any]] = None

@router.post("/events/{event_id}/check-in")
async def check_in_attendee(
    event_id: int,
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    with open("checkin_debug.txt", "a") as f:
        f.write(f"--- Check-in Request ---\n")
        f.write(f"Event ID: {event_id}\n")
        f.write(f"Ticket ID: {ticket_id}\n")
        f.write(f"Organizer: {current_user.email}\n")

    # 1. Verify Organizer (Authorization)
    event = await session.get(Event, event_id)
    if not event:
        with open("checkin_debug.txt", "a") as f: f.write("Error: Event not found\n")
        raise HTTPException(status_code=404, detail="Event not found")
        
    # Check if current user is the creator (using simple email check from raw_data)
    creator_email = event.raw_data.get("created_by") if event.raw_data else None
    if creator_email != current_user.email:
         with open("checkin_debug.txt", "a") as f: f.write(f"Error: Not authorized. Creator: {creator_email}, User: {current_user.email}\n")
         raise HTTPException(status_code=403, detail="Not authorized to check-in attendees for this event")

    # 2. Find Registration
    # Note: Ticket ID passed from frontend is the confirmation_id ("SELF-...")
    stmt = select(UserRegistration).where(
        UserRegistration.event_id == event_id,
        UserRegistration.confirmation_id == ticket_id
    )
    result = await session.execute(stmt)
    registration = result.scalars().first()
    
    if not registration:
        # Debug: Check if ticket exists at all
        ck_stmt = select(UserRegistration).where(UserRegistration.confirmation_id == ticket_id)
        ck_res = await session.execute(ck_stmt)
        ck_reg = ck_res.scalars().first()
        
        with open("checkin_debug.txt", "a") as f: 
            if ck_reg:
                f.write(f"Error: Ticket found but Event mismatch. Ticket Event ID: {ck_reg.event_id}, Request Eqvent ID: {event_id}\n")
            else:
                f.write("Error: Ticket ID not found in DB\n")

        return {
            "status": "INVALID_TICKET",
            "message": "Ticket ID not found for this event.",
            "attendee": None
        }

    # 3. Check Status
    attendee_info = {
        "name": registration.raw_data.get("attendee", {}).get("name", "Unknown"),
        "email": registration.user_email,
        "ticket_type": (
             ", ".join([f"{t.get('selectedQty')} x {t.get('name')}" for t in registration.raw_data.get("tickets", []) if t.get("selectedQty", 0) > 0])
             if registration.raw_data and "tickets" in registration.raw_data else "Standard"
        ),
        "checked_in_at": registration.checked_in_at
    }

    if registration.checked_in_at:
        return {
            "status": "ALREADY_CHECKED_IN",
            "message": f"Attendee already checked in at {registration.checked_in_at.strftime('%H:%M')}",
            "attendee": attendee_info
        }

    # 4. Perform Check-in
    registration.checked_in_at = datetime.now()
    session.add(registration)
    await session.commit()
    await session.refresh(registration)
    
    # Update returned info
    attendee_info["checked_in_at"] = registration.checked_in_at

    return {
        "status": "SUCCESS",
        "message": "Check-in Successful!",
        "attendee": attendee_info
    }
