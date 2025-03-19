from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.models.payment import PaymentStatus, PaymentType


class PaymentBase(BaseModel):
    """
    Base schema for payment data.
    """
    amount: float
    currency: str = "usd"
    status: PaymentStatus
    payment_type: PaymentType
    description: Optional[str] = None


class PaymentCreate(PaymentBase):
    """
    Schema for creating a new payment.
    """
    user_id: str
    stripe_payment_id: str
    payment_method: Optional[str] = None
    receipt_url: Optional[str] = None
    payment_metadata: Optional[str] = None  # JSON string with additional data


class PaymentUpdate(BaseModel):
    """
    Schema for updating payment data.
    """
    status: Optional[PaymentStatus] = None
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    metadata: Optional[str] = None


class PaymentResponse(PaymentBase):
    """
    Schema for payment response data.
    """
    id: str
    user_id: str
    stripe_payment_id: str
    payment_method: Optional[str] = None
    receipt_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentIntentCreateRequest(BaseModel):
    """
    Schema for creating a Stripe payment intent.
    """
    amount: float
    currency: str = "usd"
    payment_type: PaymentType
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PaymentIntentResponse(BaseModel):
    """
    Schema for payment intent response.
    """
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str
    status: str


class PaymentMethodResponse(BaseModel):
    """
    Schema for payment method response.
    """
    id: str
    type: str
    card: Optional[Dict[str, Any]] = None
    billing_details: Optional[Dict[str, Any]] = None
    created: datetime


class CustomerPaymentMethods(BaseModel):
    """
    Schema for customer payment methods response.
    """
    payment_methods: List[PaymentMethodResponse]


class WebhookPayloadResponse(BaseModel):
    """
    Schema for webhook payload response.
    """
    received: bool
    event_type: str
    details: Optional[Dict[str, Any]] = None
