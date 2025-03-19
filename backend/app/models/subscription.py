from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum, JSON, Float, Text, func
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


class SubscriptionBillingPeriod(str, enum.Enum):
    """
    Enum for subscription billing periods.
    """
    MONTHLY = "monthly"
    YEARLY = "yearly"
    QUARTERLY = "quarterly"
    LIFETIME = "lifetime"


class Subscription(Base):
    """
    Subscription model for tracking user subscriptions.
    """
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    
    # Identifiers and status
    stripe_subscription_id = Column(String, unique=True, nullable=True)
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
    
    # Billing details
    billing_period = Column(Enum(SubscriptionBillingPeriod), default=SubscriptionBillingPeriod.MONTHLY, nullable=False)
    billing_email = Column(String, nullable=True)
    billing_name = Column(String, nullable=True)
    billing_address = Column(Text, nullable=True)
    billing_country = Column(String, nullable=True)
    
    # Payment details
    amount = Column(Float, nullable=False, default=0.0)
    currency = Column(String, default="USD", nullable=False)
    payment_method_id = Column(String, nullable=True)
    payment_method_type = Column(String, nullable=True)  # e.g., "card", "paypal", etc.
    last_four = Column(String, nullable=True)  # Last 4 digits of payment method
    card_brand = Column(String, nullable=True)  # e.g., "visa", "mastercard", etc.
    
    # Subscription period
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    
    # Cancellation
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime, nullable=True)
    
    # Invoice history
    next_invoice_date = Column(DateTime, nullable=True)
    invoice_data = Column(JSON, nullable=True)  # JSON with last invoice details
    latest_invoice_id = Column(String, nullable=True)
    
    # Usage data
    usage_stats = Column(JSON, nullable=True)  # JSON with usage metrics
    
    # Metadata
    subscription_metadata = Column(JSON, nullable=True)  # Generic metadata JSON
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    subscription_plan_id = Column(String, ForeignKey("subscription_plan.id", ondelete="SET NULL"), nullable=True)
    product_id = Column(String, ForeignKey("product.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan_details = relationship("SubscriptionPlan", back_populates="subscriptions")
    product = relationship("Product")
    billing_history = relationship("BillingHistory", back_populates="subscription", cascade="all, delete-orphan")
