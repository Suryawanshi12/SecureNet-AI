from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL connection
DATABASE_URL = "postgresql://postgres:shruti1506@localhost:5432/securenet_ai"

# Create database engine
engine = create_engine(
    DATABASE_URL,
    echo=True
)

# Database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for database models
Base = declarative_base()


# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()