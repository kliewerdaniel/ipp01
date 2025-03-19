from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum, func
from sqlalchemy.orm import relationship
from uuid import uuid4
import enum

from app.db.base_class import Base


class SubscriptionStatus(str, enum.Enum):
    """
    Enum for subscription status.
    """
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"


class SubscriptionPlan(str, enum.Enum):
    """
    Enum for subscription plans.
    """
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class Subscription(Base):
    """
    Subscription model for tracking user subscriptions.
    """
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    stripe_subscription_id = Column(String, unique=True, nullable=True)
    plan = Column(Enum(SubscriptionPlan), nullable=False, default=SubscriptionPlan.FREE)
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Metadata
    plan_data = Column(String, nullable=True)  # JSON string with plan details
    
    # Foreign keys
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
