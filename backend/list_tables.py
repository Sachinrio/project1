
from sqlalchemy import create_engine, inspect
from app.core.database import DATABASE_URL

sync_url = DATABASE_URL.replace("asyncpg", "psycopg2")
engine = create_engine(sync_url)
inspector = inspect(engine)
print(inspector.get_table_names())
