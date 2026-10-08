from sqlalchemy import text
from backend.db import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✅ PostgreSQL connection successful!")
        print("Result:", result.scalar())

except Exception as e:
    print("❌ Database connection failed!")
    print("Error:", e)