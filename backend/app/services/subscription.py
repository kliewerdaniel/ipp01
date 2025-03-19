from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import logging
import json
from datetime import datetime, timedelta

from app.models.subscription import (
    Subscription, 
    SubscriptionStatus, 
    SubscriptionBillingPeriod
)
from app.models.subscription_plan import SubscriptionPlan
from app.models.billing_history import BillingHistory, BillingEventType, PaymentStatus as BillingPaymentStatus
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionCreate, 
    SubscriptionUpdate,
    PlanDetails,
    PlanFeature,
    SubscriptionResponse
)
from app.services.stripe_service import (
    get_or_create_customer,
    create_subscription as create_stripe_subscription,
    update_subscription as update_stripe_subscription,
    cancel_subscription as cancel_stripe_subscription,
    create_billing_portal_session
)
from app.services.subscription_plan_service import (
    get_plan_by_code,
    get_formatted_plans,
    get_stripe_price_id,
    sync_stripe_products_and_prices
)

logger = logging.getLogger(__name__)


def get_subscription_by_id(db: Session, id: str) -> Optional[Subscription]:
    """
    Get a subscription by ID.
    """
    return db.query(Subscription).filter(Subscription.id == id).first()


def get_subscription_by_stripe_id(db: Session, stripe_id: str) -> Optional[Subscription]:
    """
    Get a subscription by Stripe subscription ID.
    """
    return db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_id).first()


def get_active_subscription_for_user(db: Session, user_id: str) -> Optional[Subscription]:
    """
    Get the active subscription for a user.
    """
    return (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE
        )
        .order_by(desc(Subscription.created_at))
        .first()
    )


def get_user_subscriptions(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 100,
) -> List[Subscription]:
    """
    Get all subscriptions for a user.
    """
    return (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id)
        .order_by(desc(Subscription.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_subscription(db: Session, obj_in: SubscriptionCreate) -> Subscription:
    """
    Create a new subscription.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == obj_in.user_id).first()
    if not user:
        raise ValueError(f"User with ID {obj_in.user_id} not found")
    
    # Create subscription
    db_obj = Subscription(**obj_in.model_dump(exclude_unset=True))
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    logger.info(f"Created new subscription: {db_obj.id} for user {db_obj.user_id}")
    return db_obj


def update_subscription(
    db: Session, 
    db_obj: Subscription, 
    obj_in: Union[SubscriptionUpdate, Dict[str, Any]]
) -> Subscription:
    """
    Update a subscription.
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    # Update subscription with new data
    for field in update_data:
        if hasattr(db_obj, field):
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    logger.info(f"Updated subscription: {db_obj.id}")
    return db_obj


def cancel_subscription(
    db: Session, 
    db_obj: Subscription, 
    at_period_end: bool = True
) -> Subscription:
    """
    Cancel a subscription.
    """
    # Update subscription in the database
    if at_period_end:
        db_obj.cancel_at_period_end = True
    else:
        db_obj.status = SubscriptionStatus.CANCELED
        db_obj.canceled_at = datetime.utcnow()
    
    # Also cancel in Stripe if we have a Stripe subscription ID
    if db_obj.stripe_subscription_id:
        try:
            # Use the stripe_service function
            cancel_stripe_subscription(
                subscription_id=db_obj.stripe_subscription_id,
                at_period_end=at_period_end
            )
            
            logger.info(f"Canceled Stripe subscription: {db_obj.stripe_subscription_id}")
            
        except Exception as e:
            logger.error(f"Error canceling Stripe subscription: {str(e)}")
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # Create billing history record
    create_billing_history_record(
        db,
        user_id=db_obj.user_id,
        subscription_id=db_obj.id,
        event_type=BillingEventType.SUBSCRIPTION_CANCELLED,
        description=f"Subscription canceled {'at period end' if at_period_end else 'immediately'}"
    )
    
    logger.info(f"Canceled subscription: {db_obj.id}, at period end: {at_period_end}")
    return db_obj


def reactivate_subscription(db: Session, db_obj: Subscription) -> Subscription:
    """
    Reactivate a canceled subscription if it's still within the current period.
    """
    # Check if subscription is eligible for reactivation
    if db_obj.status != SubscriptionStatus.CANCELED or not db_obj.cancel_at_period_end:
        raise ValueError("Only canceled subscriptions can be reactivated")
    
    if db_obj.current_period_end and db_obj.current_period_end < datetime.utcnow():
        raise ValueError("Subscription period has already ended")
    
    # Reactivate in Stripe if we have a Stripe subscription ID
    if db_obj.stripe_subscription_id:
        try:
            # Use the stripe_service function
            update_stripe_subscription(
                subscription_id=db_obj.stripe_subscription_id,
                cancel_at_period_end=False
            )
            logger.info(f"Reactivated Stripe subscription: {db_obj.stripe_subscription_id}")
        except Exception as e:
            logger.error(f"Error reactivating Stripe subscription: {str(e)}")
    
    # Update subscription in the database
    db_obj.cancel_at_period_end = False
    db_obj.status = SubscriptionStatus.ACTIVE
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # Create billing history record
    create_billing_history_record(
        db,
        user_id=db_obj.user_id,
        subscription_id=db_obj.id,
        event_type=BillingEventType.SUBSCRIPTION_UPDATED,
        description="Subscription reactivated"
    )
    
    logger.info(f"Reactivated subscription: {db_obj.id}")
    return db_obj


def get_subscription_plans(db: Session, billing_cycle: str = "monthly") -> List[PlanDetails]:
    """
    Get all available subscription plans with proper Stripe integration.
    """
    # First, ensure all plans are synced with Stripe
    sync_stripe_products_and_prices(db)
    
    # Then get formatted plans for the frontend
    return get_formatted_plans(db, billing_cycle)


def create_subscription_with_stripe(
    db: Session,
    user_id: str,
    plan_code: str,
    payment_method_id: str,
    billing_cycle: str = "monthly"
) -> Dict[str, Any]:
    """
    Create a new subscription in Stripe and in the database.
    """
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User with ID {user_id} not found")
    
    # Check if user already has an active subscription
    existing_sub = get_active_subscription_for_user(db, user_id)
    if existing_sub:
        raise ValueError(f"User already has an active subscription")
    
    # Get plan from database
    plan = get_plan_by_code(db, plan_code)
    if not plan:
        raise ValueError(f"Plan with code {plan_code} not found")
    
    # Free plan handling (no Stripe needed)
    if plan.price_monthly == 0:
        subscription = create_subscription(
            db,
            SubscriptionCreate(
                user_id=user_id,
                subscription_plan_id=plan.id,
                status=SubscriptionStatus.ACTIVE,
                billing_period=SubscriptionBillingPeriod.MONTHLY,
                amount=0,
                currency=plan.currency,
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30),
            )
        )
        
        # Create billing history record
        create_billing_history_record(
            db,
            user_id=user_id,
            subscription_id=subscription.id,
            event_type=BillingEventType.SUBSCRIPTION_CREATED,
            description=f"Free plan activated: {plan.name}",
            amount=0,
            currency=plan.currency,
            payment_status=BillingPaymentStatus.COMPLETED
        )
        
        return {
            "subscription_id": subscription.id,
            "status": subscription.status.value,
            "current_period_end": subscription.current_period_end,
            "plan_code": plan_code,
            "requires_payment": False
        }
    
    try:
        # Get or create Stripe customer
        customer = get_or_create_customer(
            email=user.email,
            name=user.name,
            metadata={"user_id": user_id}
        )
        
        # Determine billing interval and get appropriate Stripe price ID
        interval = "year" if billing_cycle == "yearly" else "month"
        price_id = get_stripe_price_id(plan, billing_cycle)
        
        if not price_id:
            # Fallback if specific billing cycle price not found
            price_id = plan.stripe_price_id
            interval = "month"
        
        if not price_id:
            raise ValueError(f"No Stripe price defined for plan {plan_code}")
        
        # Create subscription in Stripe
        stripe_subscription = create_stripe_subscription(
            customer_id=customer.id,
            price_id=price_id,
            trial_period_days=plan.trial_days if plan.trial_days and plan.trial_days > 0 else None,
            metadata={"user_id": user_id, "plan_code": plan_code},
            expand=["latest_invoice.payment_intent"]
        )
        
        # Calculate period dates
        current_period_start = datetime.fromtimestamp(stripe_subscription.current_period_start)
        current_period_end = datetime.fromtimestamp(stripe_subscription.current_period_end)
        
        # Determine initial status
        status = SubscriptionStatus(stripe_subscription.status)
        
        # Set trial dates if applicable
        trial_start = None
        trial_end = None
        if stripe_subscription.trial_start:
            trial_start = datetime.fromtimestamp(stripe_subscription.trial_start)
            trial_end = datetime.fromtimestamp(stripe_subscription.trial_end)
            
        # Set billing period based on chosen interval
        billing_period = SubscriptionBillingPeriod.YEARLY if interval == "year" else SubscriptionBillingPeriod.MONTHLY
        
        # Create subscription in database
        subscription = create_subscription(
            db,
            SubscriptionCreate(
                user_id=user_id,
                subscription_plan_id=plan.id,
                status=status,
                stripe_subscription_id=stripe_subscription.id,
                current_period_start=current_period_start,
                current_period_end=current_period_end,
                trial_start=trial_start,
                trial_end=trial_end,
                billing_period=billing_period,
                amount=plan.price_yearly if billing_period == SubscriptionBillingPeriod.YEARLY else plan.price_monthly,
                currency=plan.currency,
                payment_method_id=payment_method_id,
                subscription_metadata=json.dumps({
                    "stripe_customer_id": customer.id,
                    "price_id": price_id
                })
            )
        )
        
        # Create billing history record
        create_billing_history_record(
            db,
            user_id=user_id,
            subscription_id=subscription.id,
            event_type=BillingEventType.SUBSCRIPTION_CREATED,
            description=f"Subscription created: {plan.name} ({billing_cycle})",
            amount=subscription.amount,
            currency=subscription.currency,
            payment_status=BillingPaymentStatus.PENDING if status == SubscriptionStatus.INCOMPLETE else BillingPaymentStatus.COMPLETED,
            payment_method_type="card",
            stripe_invoice_id=stripe_subscription.latest_invoice.id if hasattr(stripe_subscription, "latest_invoice") else None
        )
        
        # Return subscription info with client secret for payment confirmation if needed
        result = {
            "subscription_id": subscription.id,
            "stripe_subscription_id": stripe_subscription.id,
            "status": subscription.status.value,
            "current_period_end": current_period_end.isoformat(),
            "plan_code": plan_code,
            "requires_payment": status == SubscriptionStatus.INCOMPLETE
        }
        
        # Include payment info if needed
        if status == SubscriptionStatus.INCOMPLETE and hasattr(stripe_subscription, "latest_invoice") and hasattr(stripe_subscription.latest_invoice, "payment_intent"):
            result["client_secret"] = stripe_subscription.latest_invoice.payment_intent.client_secret
        
        return result
    
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise


def process_subscription_webhook(db: Session, event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process Stripe webhook events related to subscriptions.
    Returns details about the processed event.
    """
    event_type = event_data.get("type")
    
    # Return early if this is not a subscription-related event
    if not event_type.startswith("customer.subscription"):
        return {"status": "ignored", "event_type": event_type}
    
    try:
        # Get subscription data from the event
        subscription_data = event_data.get("data", {}).get("object", {})
        stripe_subscription_id = subscription_data.get("id")
        
        if not stripe_subscription_id:
            logger.error("No subscription ID in webhook event")
            return {"status": "error", "message": "No subscription ID in event"}
        
        # Find subscription in our database
        subscription = get_subscription_by_stripe_id(db, stripe_subscription_id)
        
        if not subscription:
            logger.warning(f"Subscription not found: {stripe_subscription_id}")
            return {"status": "not_found", "subscription_id": stripe_subscription_id}
        
        # Extract metadata
        user_id = subscription.user_id
        
        # Process based on event type
        if event_type == "customer.subscription.created":
            # Usually handled during creation, but add a billing record just in case
            create_billing_history_record(
                db,
                user_id=user_id,
                subscription_id=subscription.id,
                event_type=BillingEventType.SUBSCRIPTION_CREATED,
                description="Subscription created via webhook",
                stripe_event_id=event_data.get("id")
            )
            
        elif event_type == "customer.subscription.updated":
            # Extract key information
            status = SubscriptionStatus(subscription_data.get("status"))
            cancel_at_period_end = subscription_data.get("cancel_at_period_end", False)
            
            # Extract period dates
            current_period_start = datetime.fromtimestamp(subscription_data.get("current_period_start"))
            current_period_end = datetime.fromtimestamp(subscription_data.get("current_period_end"))
            
            # Extract trial dates if applicable
            trial_start = None
            trial_end = None
            if subscription_data.get("trial_start"):
                trial_start = datetime.fromtimestamp(subscription_data.get("trial_start"))
            if subscription_data.get("trial_end"):
                trial_end = datetime.fromtimestamp(subscription_data.get("trial_end"))
            
            # Handle status changes
            old_status = subscription.status
            
            # Update subscription in database
            update_data = {
                "status": status,
                "cancel_at_period_end": cancel_at_period_end,
                "current_period_start": current_period_start,
                "current_period_end": current_period_end
            }
            
            if trial_start:
                update_data["trial_start"] = trial_start
            if trial_end:
                update_data["trial_end"] = trial_end
            
            update_subscription(db, subscription, update_data)
            
            # Create billing history record based on the type of update
            event_description = "Subscription updated"
            billing_event_type = BillingEventType.SUBSCRIPTION_UPDATED
            
            # Detect specific status changes
            if old_status != status:
                if status == SubscriptionStatus.ACTIVE and old_status == SubscriptionStatus.TRIALING:
                    billing_event_type = BillingEventType.TRIAL_ENDED
                    event_description = "Trial period ended, subscription now active"
                
                elif status == SubscriptionStatus.PAST_DUE:
                    billing_event_type = BillingEventType.PAYMENT_FAILED
                    event_description = "Payment failed, subscription past due"
                
                elif status == SubscriptionStatus.CANCELED:
                    billing_event_type = BillingEventType.SUBSCRIPTION_CANCELLED
                    event_description = "Subscription canceled"
            
            # Create history record for the update
            create_billing_history_record(
                db,
                user_id=user_id,
                subscription_id=subscription.id,
                event_type=billing_event_type,
                description=event_description,
                stripe_event_id=event_data.get("id")
            )
            
        elif event_type == "customer.subscription.deleted":
            # Mark subscription as canceled
            update_subscription(
                db,
                subscription,
                {
                    "status": SubscriptionStatus.CANCELED,
                    "canceled_at": datetime.utcnow()
                }
            )
            
            # Create billing history record
            create_billing_history_record(
                db,
                user_id=user_id,
                subscription_id=subscription.id,
                event_type=BillingEventType.SUBSCRIPTION_CANCELLED,
                description="Subscription deleted",
                stripe_event_id=event_data.get("id")
            )
            
        elif event_type == "customer.subscription.trial_will_end":
            # Create notification record for trial ending soon
            create_billing_history_record(
                db,
                user_id=user_id,
                subscription_id=subscription.id,
                event_type=BillingEventType.TRIAL_ENDED,
                description="Trial period ending soon",
                stripe_event_id=event_data.get("id")
            )
        
        return {
            "status": "processed",
            "event_type": event_type,
            "subscription_id": subscription.id
        }
            
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {"status": "error", "message": str(e)}


def create_billing_history_record(
    db: Session,
    user_id: str,
    subscription_id: str,
    event_type: BillingEventType,
    description: Optional[str] = None,
    amount: Optional[float] = None,
    currency: Optional[str] = None,
    payment_status: Optional[BillingPaymentStatus] = None,
    payment_method_type: Optional[str] = None,
    payment_last_four: Optional[str] = None,
    payment_brand: Optional[str] = None,
    invoice_id: Optional[str] = None,
    invoice_url: Optional[str] = None,
    receipt_url: Optional[str] = None,
    refund_id: Optional[str] = None,
    refunded_amount: Optional[float] = None,
    refund_reason: Optional[str] = None,
    previous_plan_id: Optional[str] = None,
    new_plan_id: Optional[str] = None,
    stripe_event_id: Optional[str] = None,
    stripe_invoice_id: Optional[str] = None,
    stripe_payment_intent_id: Optional[str] = None,
    stripe_charge_id: Optional[str] = None,
    event_metadata: Optional[Dict[str, Any]] = None
) -> BillingHistory:
    """
    Create a billing history record for tracking subscription and payment events.
    """
    billing_record = BillingHistory(
        user_id=user_id,
        subscription_id=subscription_id,
        event_type=event_type,
        description=description,
        amount=amount,
        currency=currency,
        payment_status=payment_status,
        payment_method_type=payment_method_type,
        payment_last_four=payment_last_four,
        payment_brand=payment_brand,
        invoice_id=invoice_id,
        invoice_url=invoice_url,
        receipt_url=receipt_url,
        refund_id=refund_id,
        refunded_amount=refunded_amount,
        refund_reason=refund_reason,
        previous_plan_id=previous_plan_id,
        new_plan_id=new_plan_id,
        stripe_event_id=stripe_event_id,
        stripe_invoice_id=stripe_invoice_id,
        stripe_payment_intent_id=stripe_payment_intent_id,
        stripe_charge_id=stripe_charge_id,
        event_metadata=event_metadata
    )
    
    db.add(billing_record)
    db.commit()
    db.refresh(billing_record)
    
    return billing_record


def upgrade_subscription(
    db: Session,
    subscription_id: str,
    new_plan_code: str,
    billing_cycle: str = None,
    proration_behavior: str = "create_prorations"
) -> Dict[str, Any]:
    """
    Upgrade a subscription to a new plan.
    """
    # Get current subscription
    subscription = get_subscription_by_id(db, subscription_id)
    if not subscription:
        raise ValueError(f"Subscription with ID {subscription_id} not found")
    
    # Get new plan
    new_plan = get_plan_by_code(db, new_plan_code)
    if not new_plan:
        raise ValueError(f"Plan with code {new_plan_code} not found")
    
    # Get current plan
    current_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == subscription.subscription_plan_id).first()
    if not current_plan:
        raise ValueError("Current subscription plan not found")
    
    # Use the same billing cycle if not specified
    if not billing_cycle:
        billing_cycle = "yearly" if subscription.billing_period == SubscriptionBillingPeriod.YEARLY else "monthly"
    
    # Check if this is actually an upgrade
    current_price = current_plan.price_yearly if billing_cycle == "yearly" else current_plan.price_monthly
    new_price = new_plan.price_yearly if billing_cycle == "yearly" else new_plan.price_monthly
    
    if new_price < current_price:
        logger.warning(f"Downgrade detected: {current_plan.code} ({current_price}) -> {new_plan_code} ({new_price})")
    
    try:
        # Skip Stripe for free plans
        if new_plan.price_monthly == 0:
            # Just update the subscription in the database
            update_data = {
                "subscription_plan_id": new_plan.id,
                "amount": 0,
                "currency": new_plan.currency
            }
            
            updated_sub = update_subscription(db, subscription, update_data)
            
            # Create billing history record
            create_billing_history_record(
                db,
                user_id=subscription.user_id,
                subscription_id=subscription.id,
                event_type=BillingEventType.PLAN_CHANGED,
                description=f"Plan changed: {current_plan.name} -> {new_plan.name}",
                previous_plan_id=current_plan.id,
                new_plan_id=new_plan.id
            )
            
            return {
                "subscription_id": updated_sub.id,
                "status": updated_sub.status.value,
                "current_period_end": updated_sub.current_period_end.isoformat() if updated_sub.current_period_end else None,
                "plan_code": new_plan_code
            }
        
        # Handle paid plan upgrades via Stripe
        if not subscription.stripe_subscription_id:
            raise ValueError("No Stripe subscription ID found for this subscription")
        
        # Get Stripe price ID for the new plan
        new_price_id = get_stripe_price_id(new_plan, billing_cycle)
        if not new_price_id:
            raise ValueError(f"No Stripe price found for plan {new_plan_code} with {billing_cycle} billing")
        
        # Update subscription in Stripe
        stripe_subscription = update_stripe_subscription(
            subscription_id=subscription.stripe_subscription_id,
            price_id=new_price_id,
            proration_behavior=proration_behavior,
            metadata={"plan_code": new_plan_code}
        )
        
        # Update local subscription
        update_data = {
            "subscription_plan_id": new_plan.id,
            "amount": new_plan.price_yearly if billing_cycle == "yearly" else new_plan.price_monthly,
            "currency": new_plan.currency,
            "billing_period": SubscriptionBillingPeriod.YEARLY if billing_cycle == "yearly" else SubscriptionBillingPeriod.MONTHLY
        }
        
        updated_sub = update_subscription(db, subscription, update_data)
        
        # Create billing history record
        create_billing_history_record(
            db,
            user_id=subscription.user_id,
            subscription_id=subscription.id,
            event_type=BillingEventType.PLAN_CHANGED,
            description=f"Plan changed: {current_plan.name} -> {new_plan.name}",
            previous_plan_id=current_plan.id,
            new_plan_id=new_plan.id,
            amount=update_data["amount"],
            currency=update_data["currency"]
        )
        
        return {
            "subscription_id": updated_sub.id,
            "stripe_subscription_id": updated_sub.stripe_subscription_id,
            "status": updated_sub.status.value,
            "current_period_end": updated_sub.current_period_end.isoformat() if updated_sub.current_period_end else None,
            "plan_code": new_plan_code
        }
        
    except Exception as e:
        logger.error(f"Error upgrading subscription: {str(e)}")
        raise


def get_subscription_statistics(db: Session) -> Dict[str, Any]:
    """
    Get statistics on subscriptions.
    """
    # Total subscriptions
    total_subscriptions = db.query(Subscription).count()
    
    # Active subscriptions
    active_subscriptions = (
        db.query(Subscription)
        .filter(Subscription.status == SubscriptionStatus.ACTIVE)
        .count()
    )
    
    # Subscriptions by plan
    plan_counts = (
        db.query(
            SubscriptionPlan.code,
            func.count(Subscription.id).label("count")
        )
        .join(Subscription, Subscription.subscription_plan_id == SubscriptionPlan.id)
        .group_by(SubscriptionPlan.code)
        .all()
    )
    
    plan_dict = {
        plan_code: count for plan_code, count in plan_counts
    }
    
    # Get actual subscription amounts for MRR calculation
    mrr_data = (
        db.query(
            func.sum(Subscription.amount).label("total_amount")
        )
        .filter(
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.billing_period == SubscriptionBillingPeriod.MONTHLY
        )
        .scalar() or 0
    )
    
    # Add yearly subscriptions divided by 12
    yearly_mrr = (
        db.query(
            func.sum(Subscription.amount / 12).label("yearly_amount")
        )
        .filter(
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.billing_period == SubscriptionBillingPeriod.YEARLY
        )
        .scalar() or 0
    )
    
    mrr = float(mrr_data) + float(yearly_mrr)
    
    return {
        "total_subscriptions": total_subscriptions,
        "active_subscriptions": active_subscriptions,
        "by_plan": plan_dict,
        "mrr": round(mrr, 2)
    }


def create_billing_portal_session_url(db: Session, user_id: str, return_url: str) -> str:
    """
    Create a Stripe billing portal session for a user to manage their subscription.
    """
    # Get user's active subscription
    subscription = get_active_subscription_for_user(db, user_id)
    if not subscription:
        raise ValueError("No active subscription found for this user")
    
    # Extract Stripe customer ID from subscription metadata
    if not subscription.subscription_metadata:
        raise ValueError("No subscription metadata found")
    
    try:
        metadata = json.loads(subscription.subscription_metadata)
        customer_id = metadata.get("stripe_customer_id")
        
        if not customer_id:
            raise ValueError("No Stripe customer ID found in subscription metadata")
        
        # Create billing portal session
        session = create_billing_portal_session(
            customer_id=customer_id,
            return_url=return_url
        )
        
        return session.url
        
    except Exception as e:
        logger.error(f"Error creating billing portal session: {str(e)}")
        raise
