from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create a database engine
engine = create_engine(
    settings.DATABASE_URL,
    # Connect args for PostgreSQL
    connect_args={} if "postgresql" in settings.DATABASE_URL else {"check_same_thread": False}
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get a DB session
def get_db():
    """
    Dependency function to get a database session.
    
    This function creates a new database session for each request
    and closes it once the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
