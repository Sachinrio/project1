import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql+asyncpg://postgres:Sankar%40722001@localhost:5432/infinitetechai"

# Force sync for this script
if "+asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")
elif DATABASE_URL.startswith("postgresql+asyncpg://"):
     DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

def check_db():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT count(*) FROM user"))
        print(f"Users Count (SQL): {result.scalar()}")
        
        result_events = conn.execute(text("SELECT count(*) FROM event"))
        print(f"Events Count (SQL): {result_events.scalar()}")

if __name__ == "__main__":
    check_db()
