from fastapi import APIRouter, Depends, HTTPException, status, Request, Body, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import json

from app.db.session import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.payment import PaymentType, PaymentStatus
from app.models.subscription import SubscriptionPlan, SubscriptionStatus
from app.schemas.payment import (
    PaymentResponse,
    PaymentIntentCreateRequest,
    PaymentIntentResponse,
    PaymentMethodResponse,
    CustomerPaymentMethods,
    WebhookPayloadResponse
)
from app.schemas.subscription import (
    SubscriptionResponse,
    SubscriptionCreateRequest,
    SubscriptionCancelRequest,
    PlanDetails
)
from app.services.payment import (
    get_payment_by_id,
    get_user_payments,
    create_payment_intent,
    get_payment_methods,
    process_payment_webhook
)
from app.services.subscription import (
    get_subscription_by_id,
    get_active_subscription_for_user,
    get_user_subscriptions,
    create_stripe_subscription,
    cancel_subscription,
    reactivate_subscription,
    get_subscription_plans,
    process_stripe_webhook
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/subscription/plans", response_model=List[PlanDetails])
async def list_subscription_plans(
    current_user: dict = Depends(get_current_user),
):
    """
    Get available subscription plans.
    """
    return get_subscription_plans()


@router.get("/subscription/my", response_model=Optional[SubscriptionResponse])
async def get_my_subscription(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's active subscription.
    """
    subscription = get_active_subscription_for_user(db, current_user["id"])
    return subscription


@router.get("/subscription/history", response_model=List[SubscriptionResponse])
async def get_subscription_history(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get subscription history for the current user.
    """
    subscriptions = get_user_subscriptions(
        db,
        user_id=current_user["id"],
        skip=skip,
        limit=limit
    )
    return subscriptions


@router.post("/subscription", status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_request: SubscriptionCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new subscription.
    """
    try:
        subscription_data = create_stripe_subscription(
            db,
            user_id=current_user["id"],
            plan=subscription_request.plan,
            payment_method_id=subscription_request.payment_method_id
        )
        return subscription_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription"
        )


@router.post("/subscription/{subscription_id}/cancel", response_model=SubscriptionResponse)
async def cancel_subscription_endpoint(
    subscription_id: str,
    cancel_request: SubscriptionCancelRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a subscription.
    """
    subscription = get_subscription_by_id(db, subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription with ID {subscription_id} not found"
        )
    
    # Verify ownership
    if subscription.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel this subscription"
        )
    
    try:
        canceled_subscription = cancel_subscription(
            db,
            db_obj=subscription,
            at_period_end=cancel_request.at_period_end
        )
        return canceled_subscription
    except Exception as e:
        logger.error(f"Error canceling subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )


@router.post("/subscription/{subscription_id}/reactivate", response_model=SubscriptionResponse)
async def reactivate_subscription_endpoint(
    subscription_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reactivate a canceled subscription.
    """
    subscription = get_subscription_by_id(db, subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription with ID {subscription_id} not found"
        )
    
    # Verify ownership
    if subscription.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to reactivate this subscription"
        )
    
    try:
        reactivated_subscription = reactivate_subscription(db, db_obj=subscription)
        return reactivated_subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error reactivating subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reactivate subscription"
        )


@router.get("/history", response_model=List[PaymentResponse])
async def get_payment_history(
    skip: int = 0,
    limit: int = 100,
    payment_type: Optional[PaymentType] = None,
    status: Optional[PaymentStatus] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payment history for the current user.
    """
    payments = get_user_payments(
        db,
        user_id=current_user["id"],
        skip=skip,
        limit=limit,
        payment_type=payment_type,
        status=status
    )
    return payments


@router.post("/create-payment-intent", response_model=PaymentIntentResponse)
async def create_payment_intent_endpoint(
    payment_intent_request: PaymentIntentCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a payment intent for one-time payments.
    """
    try:
        payment_intent = create_payment_intent(
            user_id=current_user["id"],
            amount=payment_intent_request.amount,
            currency=payment_intent_request.currency,
            payment_type=payment_intent_request.payment_type,
            description=payment_intent_request.description,
            metadata=payment_intent_request.metadata
        )
        return payment_intent
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment intent"
        )


@router.get("/payment-methods", response_model=CustomerPaymentMethods)
async def get_payment_methods_endpoint(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get saved payment methods for the current user.
    """
    # In a real application, you would store the customer ID in the database
    # For this example, we'll use a fake customer ID
    try:
        # Get active subscription to get customer ID
        subscription = get_active_subscription_for_user(db, current_user["id"])
        if not subscription or not subscription.plan_data:
            # No subscription with customer ID, return empty list
            return CustomerPaymentMethods(payment_methods=[])
        
        # Parse plan data to get customer ID
        plan_data = json.loads(subscription.plan_data)
        customer_id = plan_data.get("stripe_customer_id")
        
        if not customer_id:
            return CustomerPaymentMethods(payment_methods=[])
        
        # Get payment methods
        payment_methods = get_payment_methods(
            user_id=current_user["id"],
            stripe_customer_id=customer_id
        )
        
        return CustomerPaymentMethods(payment_methods=payment_methods)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting payment methods: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get payment methods"
        )


@router.post("/webhook", response_model=WebhookPayloadResponse)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    """
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe webhook is not configured"
        )
    
    try:
        # Read the request body
        payload = await request.body()
        payload_str = payload.decode("utf-8")
        
        # Verify webhook signature in a real implementation
        # For this example, we'll just parse the payload
        
        event_data = json.loads(payload_str)
        event_type = event_data.get("type", "")
        
        # Process different types of events
        if event_type.startswith("customer.subscription"):
            # Handle subscription events
            result = process_stripe_webhook(event_data)
            return WebhookPayloadResponse(
                received=True,
                event_type=event_type
            )
        
        elif event_type.startswith("payment_intent") or event_type.startswith("charge"):
            # Handle payment events
            result = process_payment_webhook(db, event_data)
            return WebhookPayloadResponse(
                received=True,
                event_type=event_type
            )
        
        # Unhandled event type
        return WebhookPayloadResponse(
            received=True,
            event_type=event_type
        )
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook error: {str(e)}"
        )
