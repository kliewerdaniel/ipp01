from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.billing_history import BillingEventType
from app.schemas.subscription import (
    SubscriptionResponse,
    SubscriptionCreateRequest,
    SubscriptionCancelRequest,
    SubscriptionUpgradeRequest,
    BillingPortalRequest,
    BillingPortalResponse,
    BillingHistoryResponse,
    PlanDetails
)
from app.services.subscription import (
    get_subscription_by_id,
    get_active_subscription_for_user,
    get_user_subscriptions,
    create_subscription_with_stripe,
    cancel_subscription,
    reactivate_subscription,
    upgrade_subscription as upgrade_subscription_service,
    get_subscription_plans,
    create_billing_portal_session_url
)
from app.services.billing_history import get_user_billing_history

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/plans", response_model=List[PlanDetails])
async def list_subscription_plans(
    billing_cycle: str = "monthly",
    db: Session = Depends(get_db)
):
    """
    Get available subscription plans.
    """
    return get_subscription_plans(db, billing_cycle)


@router.get("/my", response_model=Optional[SubscriptionResponse])
async def get_my_subscription(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's active subscription.
    """
    subscription = get_active_subscription_for_user(db, current_user["id"])
    return subscription


@router.get("/history", response_model=List[SubscriptionResponse])
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


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_request: SubscriptionCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new subscription.
    """
    try:
        subscription_data = create_subscription_with_stripe(
            db,
            user_id=current_user["id"],
            plan_code=subscription_request.plan_code,
            payment_method_id=subscription_request.payment_method_id,
            billing_cycle=subscription_request.billing_cycle
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


@router.post("/{subscription_id}/cancel", response_model=SubscriptionResponse)
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


@router.post("/{subscription_id}/reactivate", response_model=SubscriptionResponse)
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


@router.post("/{subscription_id}/upgrade", response_model=SubscriptionResponse)
async def upgrade_subscription(
    subscription_id: str,
    upgrade_request: SubscriptionUpgradeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade or downgrade a subscription to a different plan.
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
            detail="You don't have permission to modify this subscription"
        )
    
    try:
        result = upgrade_subscription_service(
            db,
            subscription_id=subscription_id,
            new_plan_code=upgrade_request.new_plan_code,
            billing_cycle=upgrade_request.billing_cycle,
            proration_behavior=upgrade_request.proration_behavior
        )
        
        # Get updated subscription to return
        updated_subscription = get_subscription_by_id(db, subscription_id)
        return updated_subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error upgrading subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upgrade subscription"
        )


@router.post("/billing-portal", response_model=BillingPortalResponse)
async def create_billing_portal(
    request: BillingPortalRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe billing portal session for managing subscriptions.
    """
    try:
        portal_url = create_billing_portal_session_url(
            db,
            user_id=current_user["id"],
            return_url=request.return_url
        )
        
        return BillingPortalResponse(url=portal_url)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating billing portal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create billing portal"
        )


@router.get("/billing-history", response_model=List[BillingHistoryResponse])
async def get_billing_history(
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[BillingEventType] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get billing history for the current user.
    """
    try:
        history = get_user_billing_history(
            db,
            user_id=current_user["id"],
            skip=skip,
            limit=limit,
            event_type=event_type
        )
        return history
    except Exception as e:
        logger.error(f"Error retrieving billing history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve billing history"
        )
