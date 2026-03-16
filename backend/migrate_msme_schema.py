import asyncio
import sys
from sqlmodel import SQLModel, Session, text
from sqlalchemy import create_engine
import os

# Set up synchronous engine for migration
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.db")
engine = create_engine(f"sqlite:///{db_path}")

def migrate():
    print("Migrating schema...")
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN itr_filed VARCHAR;"))
            conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN has_gstin VARCHAR;"))
            conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN mobile_number VARCHAR;"))
            conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN email VARCHAR;"))
            conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN social_category VARCHAR;"))
            conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN gender VARCHAR;"))
            conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN specially_abled VARCHAR;"))
            conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN enterprise_name VARCHAR;"))
            conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN plant_name VARCHAR;"))
            conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN plant_address VARCHAR;"))
            conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN official_address VARCHAR;"))
            conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN previous_registration VARCHAR;"))
            conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN date_of_incorporation VARCHAR;"))
            conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN business_commenced VARCHAR;"))
            conn.execute(text("ALTER TABLE msmeregistration ADD COLUMN date_of_commencement VARCHAR;"))
            print("Successfully added Phase 2 fields.")
        except Exception as e:
            print(f"Error (column might already exist): {e}")

if __name__ == "__main__":
    migrate()
