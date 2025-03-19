from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float, JSON, func
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.db.base_class import Base


class SubscriptionPlan(Base):
    """
    SubscriptionPlan model for defining different subscription tiers and their features.
    """
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)  # e.g., "Free", "Basic", "Premium"
    code = Column(String, unique=True, nullable=False)  # Machine-readable code
    description = Column(Text, nullable=True)
    
    # Pricing
    price_monthly = Column(Float, nullable=False, default=0.0)
    price_yearly = Column(Float, nullable=True)  # Optional; yearly discount
    currency = Column(String, default="USD", nullable=False)
    trial_days = Column(Integer, default=0, nullable=False)
    setup_fee = Column(Float, default=0.0, nullable=False)
    
    # Limits
    max_interviews = Column(Integer, nullable=True)
    max_questions_per_interview = Column(Integer, nullable=True)
    max_storage_gb = Column(Float, nullable=True)
    max_audio_length_mins = Column(Integer, nullable=True)
    
    # Features
    features = Column(JSON, nullable=True)  # JSON list of features included in this plan
    is_ai_feedback_enabled = Column(Boolean, default=False)
    is_export_enabled = Column(Boolean, default=False)
    is_team_access_enabled = Column(Boolean, default=False)
    is_premium_questions_enabled = Column(Boolean, default=False)
    is_custom_branding_enabled = Column(Boolean, default=False)
    
    # Display and ordering
    is_public = Column(Boolean, default=True)  # Whether plan appears in public pricing page
    is_active = Column(Boolean, default=True)  # Whether plan can be subscribed to
    highlight = Column(Boolean, default=False)  # Whether to highlight in pricing table
    sort_order = Column(Integer, default=0)  # Order in pricing display
    
    # Stripe integration
    stripe_price_id = Column(String, nullable=True)
    stripe_product_id = Column(String, nullable=True)
    
    # For multi-platform support
    product_id = Column(String, ForeignKey("product.id", ondelete="CASCADE"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="subscription_plans")
    subscriptions = relationship("Subscription", back_populates="plan_details", cascade="all, delete-orphan")
