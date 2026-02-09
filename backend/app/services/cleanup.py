from datetime import datetime
from sqlalchemy import or_, delete
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import Event, UserRegistration, TicketClass

async def delete_expired_events(session: AsyncSession):
    """
    Deletes events where end_time < current_time.
    If end_time is NULL, falls back to start_time < current_time.
    """
    now = datetime.now()
    
    # Logic: Delete if (end_time is NOT NULL and < now) OR (end_time is NULL and start_time < now)
    statement = select(Event).where(
        or_(
            Event.end_time < now,
            (Event.end_time == None) & (Event.start_time < now)
        )
    )
    
    result = await session.execute(statement)
    expired_events = result.scalars().all()
    
    expired_event_ids = [e.id for e in expired_events if e.id is not None]
    
    if expired_event_ids:
        # 1. Delete associated registrations first (References TicketClass and Event)
        await session.execute(
            delete(UserRegistration).where(UserRegistration.event_id.in_(expired_event_ids))
        )

        # 2. Delete related TicketClass records (References Event)
        await session.execute(
            delete(TicketClass).where(TicketClass.event_id.in_(expired_event_ids))
        )
    
    count = 0
    for event in expired_events:
        await session.delete(event)
        count += 1
    
    await session.commit()
    return count