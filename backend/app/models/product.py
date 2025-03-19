from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Float, func
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.db.base_class import Base


class Product(Base):
    """
    Product/Platform model for managing multiple interview platforms.
    """
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)  # URL-friendly unique identifier
    description = Column(Text, nullable=True)
    
    # Features and Configuration
    features = Column(JSON, nullable=True)  # JSON list of enabled features
    configuration = Column(JSON, nullable=True)  # Product-specific configuration
    custom_domains = Column(String, nullable=True)  # Comma-separated list of custom domains
    theme_settings = Column(JSON, nullable=True)  # JSON with theme options (colors, logos, etc.)
    
    # Access control
    is_public = Column(Boolean, default=True)  # Whether product is publicly accessible
    is_active = Column(Boolean, default=True)  # Whether product is currently active
    access_code = Column(String, nullable=True)  # Optional access code for private products
    
    # Customization
    custom_welcome_message = Column(Text, nullable=True)
    custom_footer = Column(Text, nullable=True)
    custom_css = Column(Text, nullable=True)
    custom_js = Column(Text, nullable=True)
    
    # Analytics
    total_users = Column(Integer, default=0)
    total_interviews = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    average_rating = Column(Float, nullable=True)
    
    # Owner/Admin
    owner_id = Column(String, nullable=True)  # Foreign key to a user, made nullable for system products
    admin_emails = Column(String, nullable=True)  # Comma-separated emails with admin access
    
    # Limits
    max_users = Column(Integer, nullable=True)
    max_interviews_per_user = Column(Integer, nullable=True)
    max_questions_per_interview = Column(Integer, nullable=True)
    max_storage_gb = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    questions = relationship("Question", back_populates="product")
    subscription_plans = relationship("SubscriptionPlan", back_populates="product", cascade="all, delete-orphan")
