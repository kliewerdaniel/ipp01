from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum, func
from sqlalchemy.orm import relationship
from uuid import uuid4
import enum

from app.db.base_class import Base


class PaymentStatus(str, enum.Enum):
    """
    Enum for payment status.
    """
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentType(str, enum.Enum):
    """
    Enum for payment types.
    """
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    UPGRADE = "upgrade"
    ADDON = "addon"


class Payment(Base):
    """
    Payment model for tracking user payments.
    """
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    stripe_payment_id = Column(String, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="usd")
    status = Column(Enum(PaymentStatus), nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False)
    description = Column(String, nullable=True)
    metadata = Column(String, nullable=True)  # JSON string with additional data
    payment_method = Column(String, nullable=True)  # e.g., "card", "bank_transfer"
    receipt_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="payments")
