from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float, Text, JSON, Boolean, func
from sqlalchemy.orm import relationship
from uuid import uuid4
import enum

from app.db.base_class import Base


class BillingEventType(str, enum.Enum):
    """
    Enum for billing event types.
    """
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_UPDATED = "subscription_updated"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    PAYMENT_SUCCEEDED = "payment_succeeded"
    PAYMENT_FAILED = "payment_failed"
    INVOICE_CREATED = "invoice_created"
    INVOICE_PAID = "invoice_paid"
    INVOICE_PAYMENT_FAILED = "invoice_payment_failed"
    REFUND_PROCESSED = "refund_processed"
    TRIAL_STARTED = "trial_started"
    TRIAL_ENDED = "trial_ended"
    PLAN_CHANGED = "plan_changed"


class PaymentStatus(str, enum.Enum):
    """
    Enum for payment status.
    """
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"


class BillingHistory(Base):
    """
    BillingHistory model for storing the billing and payment history.
    """
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    
    # Event information
    event_type = Column(Enum(BillingEventType), nullable=False)
    description = Column(Text, nullable=True)
    
    # Amount and payment
    amount = Column(Float, nullable=True)
    currency = Column(String, default="USD", nullable=True)
    payment_status = Column(Enum(PaymentStatus), nullable=True)
    
    # Payment details
    payment_method_type = Column(String, nullable=True)  # e.g., "card", "paypal"
    payment_last_four = Column(String, nullable=True)  # Last 4 digits
    payment_brand = Column(String, nullable=True)  # e.g., "visa", "mastercard"
    
    # Invoice details
    invoice_id = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True)
    invoice_url = Column(String, nullable=True)
    receipt_url = Column(String, nullable=True)
    
    # For refunds
    refund_id = Column(String, nullable=True)
    refunded_amount = Column(Float, nullable=True)
    refund_reason = Column(Text, nullable=True)
    
    # For subscription changes
    previous_plan_id = Column(String, nullable=True)
    new_plan_id = Column(String, nullable=True)
    
    # External IDs
    stripe_event_id = Column(String, nullable=True)
    stripe_invoice_id = Column(String, nullable=True)
    stripe_payment_intent_id = Column(String, nullable=True)
    stripe_charge_id = Column(String, nullable=True)
    
    # Metadata
    event_metadata = Column(JSON, nullable=True)  # Additional event metadata
    is_visible_to_customer = Column(Boolean, default=True)  # Whether to show in customer billing history
    
    # Timestamps
    event_time = Column(DateTime, default=func.now(), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(String, ForeignKey("subscription.id", ondelete="CASCADE"), nullable=True)
    
    # Relationships
    user = relationship("User")
    subscription = relationship("Subscription", back_populates="billing_history")
