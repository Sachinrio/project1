from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.schemas import User, Event
from app.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats")
async def get_dashboard_stats(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    print(f"ADMIN STATS REQUEST from {current_user.email}")
    
    # 1. Total Users
    result_users = await session.execute(select(func.count(User.id)))
    total_users = result_users.scalar()
    print(f"DEBUG: Total Users from DB: {total_users}")

    # 2. Active Events
    result_events = await session.execute(select(func.count(Event.id)))
    total_events = result_events.scalar()
    print(f"DEBUG: Total Events from DB: {total_events}")

    # 3. Free Events
    result_free = await session.execute(select(func.count(Event.id)).where(Event.is_free == True))
    free_events = result_free.scalar()

    # 4. Auto-Registered (Count of UserRegistration)
    # Assuming UserRegistration table tracks this. Including import if needed.
    from app.models.schemas import UserRegistration
    result_registrations = await session.execute(select(func.count(UserRegistration.id)))
    auto_registered = result_registrations.scalar()
    
    # 5. Recent Events (Fetch more details)
    result_recent = await session.execute(
        select(Event).order_by(Event.start_time.asc()).limit(10)
    )
    recent_events = result_recent.scalars().all()

    return {
        "total_users": total_users,
        "active_events": total_events,
        "free_events": free_events,
        "auto_registered": auto_registered,
        "recent_events": recent_events
    }

@router.get("/users")
async def get_users(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    print(f"ADMIN USERS REQUEST from {current_user.email}")
    result = await session.execute(select(User).order_by(User.id))
    users = result.scalars().all()
    return users

@router.get("/events")
async def get_events(
    page: int = 1,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    offset = (page - 1) * limit
    
    # Total Count
    count_res = await session.execute(select(func.count(Event.id)))
    total = count_res.scalar()
    
    # Paginated Events
    result = await session.execute(
        select(Event)
        .order_by(Event.start_time.asc())
        .offset(offset)
        .limit(limit)
    )
    events = result.scalars().all()
    
    return {
        "data": events,
        "total": total,
        "page": page,
        "limit": limit
    }
