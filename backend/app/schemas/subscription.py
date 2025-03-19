from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from app.models.subscription import SubscriptionStatus, SubscriptionBillingPeriod
from app.models.billing_history import BillingEventType, PaymentStatus


class SubscriptionBase(BaseModel):
    """
    Base schema for subscription data.
    """
    subscription_plan_id: Optional[str] = None
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    billing_period: SubscriptionBillingPeriod = SubscriptionBillingPeriod.MONTHLY
    amount: float = 0.0
    currency: str = "usd"


class SubscriptionCreate(SubscriptionBase):
    """
    Schema for creating a new subscription in the database.
    """
    user_id: str
    stripe_subscription_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    payment_method_id: Optional[str] = None
    subscription_metadata: Optional[str] = None  # JSON string with additional data


class SubscriptionUpdate(BaseModel):
    """
    Schema for updating subscription data.
    """
    subscription_plan_id: Optional[str] = None
    status: Optional[SubscriptionStatus] = None
    billing_period: Optional[SubscriptionBillingPeriod] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    cancel_at_period_end: Optional[bool] = None
    canceled_at: Optional[datetime] = None
    payment_method_id: Optional[str] = None
    subscription_metadata: Optional[str] = None


class SubscriptionResponse(SubscriptionBase):
    """
    Schema for subscription response data.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    
    # Plan details
    plan_details: Optional[Dict[str, Any]] = None
    
    # Stripe details
    stripe_subscription_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    payment_method_type: Optional[str] = None
    last_four: Optional[str] = None
    card_brand: Optional[str] = None
    
    # Subscription period
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    
    # Cancellation
    cancel_at_period_end: bool = False
    canceled_at: Optional[datetime] = None
    
    # Invoice data
    next_invoice_date: Optional[datetime] = None
    latest_invoice_id: Optional[str] = None
    
    # Metadata
    subscription_metadata: Optional[Dict[str, Any]] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime


class SubscriptionCreateRequest(BaseModel):
    """
    Schema for subscription creation request from the frontend.
    """
    plan_code: str
    payment_method_id: str
    billing_cycle: str = "monthly"  # "monthly" or "yearly"


class SubscriptionCancelRequest(BaseModel):
    """
    Schema for subscription cancellation request.
    """
    at_period_end: bool = True


class SubscriptionUpgradeRequest(BaseModel):
    """
    Schema for subscription upgrade or downgrade request.
    """
    new_plan_code: str
    billing_cycle: Optional[str] = None  # If not provided, keep the same
    proration_behavior: str = "create_prorations"  # Stripe proration behavior


class BillingPortalRequest(BaseModel):
    """
    Schema for creating a billing portal session.
    """
    return_url: str


class BillingPortalResponse(BaseModel):
    """
    Schema for billing portal session response.
    """
    url: str


class SubscriptionWebhookPayload(BaseModel):
    """
    Schema for Stripe webhook payload processing.
    """
    type: str
    data: Dict[str, Any]


class PlanFeature(BaseModel):
    """
    Schema for subscription plan features.
    """
    name: str
    description: str
    included: bool


class PlanDetails(BaseModel):
    """
    Schema for detailed plan information.
    """
    id: str
    name: str
    description: str
    price: float
    currency: str = "usd"
    interval: str  # 'month' or 'year'
    features: List[PlanFeature]
    popular: bool = False
    trial_days: int = 0


class BillingHistoryResponse(BaseModel):
    """
    Schema for billing history records.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    subscription_id: Optional[str] = None
    
    # Event information
    event_type: BillingEventType
    description: Optional[str] = None
    event_time: datetime
    
    # Amount and payment
    amount: Optional[float] = None
    currency: Optional[str] = None
    payment_status: Optional[PaymentStatus] = None
    
    # Payment details
    payment_method_type: Optional[str] = None
    payment_last_four: Optional[str] = None
    payment_brand: Optional[str] = None
    
    # Invoice details
    invoice_id: Optional[str] = None
    invoice_url: Optional[str] = None
    receipt_url: Optional[str] = None
    
    # For refunds
    refund_id: Optional[str] = None
    refunded_amount: Optional[float] = None
    
    # For subscription changes
    previous_plan_id: Optional[str] = None
    new_plan_id: Optional[str] = None
    
    # Visibility
    is_visible_to_customer: bool = True
    
    # Timestamps
    created_at: datetime
