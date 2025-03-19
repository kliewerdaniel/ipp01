from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from app.models.subscription import SubscriptionPlan, SubscriptionStatus


class SubscriptionBase(BaseModel):
    """
    Base schema for subscription data.
    """
    plan: SubscriptionPlan
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE


class SubscriptionCreate(SubscriptionBase):
    """
    Schema for creating a new subscription.
    """
    user_id: str
    stripe_subscription_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    plan_data: Optional[str] = None  # JSON string with plan details


class SubscriptionUpdate(BaseModel):
    """
    Schema for updating subscription data.
    """
    plan: Optional[SubscriptionPlan] = None
    status: Optional[SubscriptionStatus] = None
    stripe_subscription_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: Optional[bool] = None
    canceled_at: Optional[datetime] = None
    plan_data: Optional[str] = None


class SubscriptionResponse(SubscriptionBase):
    """
    Schema for subscription response data.
    """
    id: str
    user_id: str
    stripe_subscription_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool
    canceled_at: Optional[datetime] = None
    plan_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionCreateRequest(BaseModel):
    """
    Schema for subscription creation request from the frontend.
    """
    plan: SubscriptionPlan
    payment_method_id: str


class SubscriptionCancelRequest(BaseModel):
    """
    Schema for subscription cancellation request.
    """
    at_period_end: bool = True


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
    features: list[PlanFeature]
    popular: bool = False
    trial_days: int = 0
