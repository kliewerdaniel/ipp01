from sqlalchemy.orm import Session
import logging

from app.db.base import Base
from app.db.session import engine
from app.core.config import settings
from app.models.user import User
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """Initialize the database with tables and initial data."""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Check if the admin user already exists
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    
    # Create admin user if it doesn't exist
    if not admin_user:
        admin_user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin12345"),
            name="Admin User",
            is_active=True,
            is_superuser=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        logger.info("Created admin user")


def check_and_init_db() -> None:
    """Check and initialize database on application startup."""
    try:
        # Initialize database session
        from app.db.session import SessionLocal
        db = SessionLocal()
        
        try:
            # Initialize database
            init_db(db)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
