import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from app.models.schemas import User

# Connection String
DATABASE_URL = "postgresql+asyncpg://postgres:Sankar%40722001@localhost:5432/infinitetechai"

async def view_users():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    try:
        async with async_session() as session:
            result = await session.execute(select(User).order_by(User.id))
            users = result.scalars().all()
            
            print("\n" + "="*80)
            print(f"{'ID':<5} | {'EMAIL':<35} | {'PASSWORD HASH'}")
            print("="*80)
            
            for u in users:
                pwd_display = u.hashed_password[:30] + "..." if u.hashed_password else "OAuth User"
                print(f"{u.id:<5} | {u.email:<35} | {pwd_display}")
            print("="*80 + "\n")
                
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(view_users())
