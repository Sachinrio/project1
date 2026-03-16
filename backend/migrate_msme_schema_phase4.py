import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.db")

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Add the major_activity_under_services column. 
        # Since it's Optional[str], it allows NULL.
        cursor.execute("ALTER TABLE msmeregistration ADD COLUMN major_activity_under_services VARCHAR;")
        print("Successfully added 'major_activity_under_services' column.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column 'major_activity_under_services' already exists.")
        else:
            print(f"Error executing migration: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
