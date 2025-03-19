from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import logging
import stripe
import json
from datetime import datetime, timedelta

from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionCreate, 
    SubscriptionUpdate,
    PlanDetails,
    PlanFeature
)
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Stripe client
if settings.STRIPE_API_KEY:
    stripe.api_key = settings.STRIPE_API_KEY
else:
    logger.warning("Stripe API key not configured. Stripe functionality will be limited.")


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
    db_obj = Subscription(
        user_id=obj_in.user_id,
        plan=obj_in.plan,
        status=obj_in.status,
        stripe_subscription_id=obj_in.stripe_subscription_id,
        current_period_start=obj_in.current_period_start,
        current_period_end=obj_in.current_period_end,
        plan_data=obj_in.plan_data,
        cancel_at_period_end=False,
    )
    
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
    if db_obj.stripe_subscription_id and settings.STRIPE_API_KEY:
        try:
            stripe_sub = stripe.Subscription.retrieve(db_obj.stripe_subscription_id)
            
            if at_period_end:
                # Cancel at period end
                stripe.Subscription.modify(
                    db_obj.stripe_subscription_id,
                    cancel_at_period_end=True
                )
            else:
                # Cancel immediately
                stripe.Subscription.delete(db_obj.stripe_subscription_id)
            
            logger.info(f"Canceled Stripe subscription: {db_obj.stripe_subscription_id}")
            
        except Exception as e:
            logger.error(f"Error canceling Stripe subscription: {str(e)}")
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
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
    if db_obj.stripe_subscription_id and settings.STRIPE_API_KEY:
        try:
            stripe.Subscription.modify(
                db_obj.stripe_subscription_id,
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
    
    logger.info(f"Reactivated subscription: {db_obj.id}")
    return db_obj


def get_subscription_plans() -> List[PlanDetails]:
    """
    Get all available subscription plans.
    """
    # Define hardcoded plans
    plans = [
        PlanDetails(
            id="free",
            name="Free",
            description="Basic access to practice interviews",
            price=0.0,
            currency="usd",
            interval="month",
            features=[
                PlanFeature(
                    name="Practice Interviews",
                    description="Limited access to practice interviews",
                    included=True
                ),
                PlanFeature(
                    name="AI Feedback",
                    description="Basic AI feedback on your answers",
                    included=True
                ),
                PlanFeature(
                    name="Interview History",
                    description="Access to your last 5 interviews",
                    included=True
                ),
                PlanFeature(
                    name="Premium Question Bank",
                    description="Access to premium interview questions",
                    included=False
                ),
                PlanFeature(
                    name="Advanced Analytics",
                    description="Detailed performance analytics",
                    included=False
                ),
            ],
            trial_days=0,
        ),
        PlanDetails(
            id="basic",
            name="Basic",
            description="Enhanced interview preparation for serious candidates",
            price=9.99,
            currency="usd",
            interval="month",
            features=[
                PlanFeature(
                    name="Practice Interviews",
                    description="Unlimited access to practice interviews",
                    included=True
                ),
                PlanFeature(
                    name="AI Feedback",
                    description="Detailed AI feedback on your answers",
                    included=True
                ),
                PlanFeature(
                    name="Interview History",
                    description="Access to your full interview history",
                    included=True
                ),
                PlanFeature(
                    name="Premium Question Bank",
                    description="Access to premium interview questions",
                    included=True
                ),
                PlanFeature(
                    name="Advanced Analytics",
                    description="Detailed performance analytics",
                    included=False
                ),
            ],
            trial_days=7,
        ),
        PlanDetails(
            id="premium",
            name="Premium",
            description="Comprehensive interview preparation platform",
            price=19.99,
            currency="usd",
            interval="month",
            features=[
                PlanFeature(
                    name="Practice Interviews",
                    description="Unlimited access to practice interviews",
                    included=True
                ),
                PlanFeature(
                    name="AI Feedback",
                    description="Advanced AI feedback with improvement suggestions",
                    included=True
                ),
                PlanFeature(
                    name="Interview History",
                    description="Access to your full interview history",
                    included=True
                ),
                PlanFeature(
                    name="Premium Question Bank",
                    description="Access to premium interview questions",
                    included=True
                ),
                PlanFeature(
                    name="Advanced Analytics",
                    description="Detailed performance analytics",
                    included=True
                ),
                PlanFeature(
                    name="Expert Review",
                    description="Monthly expert review of your interviews",
                    included=True
                ),
            ],
            popular=True,
            trial_days=7,
        ),
    ]
    
    return plans


def create_stripe_subscription(
    db: Session,
    user_id: str,
    plan: SubscriptionPlan,
    payment_method_id: str
) -> Dict[str, Any]:
    """
    Create a new subscription in Stripe and in the database.
    """
    if not settings.STRIPE_API_KEY:
        raise ValueError("Stripe API key not configured")
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User with ID {user_id} not found")
    
    # Check if user already has an active subscription
    existing_sub = get_active_subscription_for_user(db, user_id)
    if existing_sub:
        raise ValueError(f"User already has an active subscription")
    
    try:
        # Map our plans to Stripe price IDs
        # In a real implementation, these would be stored in a database or environment variables
        plan_to_price_id = {
            SubscriptionPlan.FREE: None,  # Free plan doesn't need Stripe
            SubscriptionPlan.BASIC: "price_basic",  # This would be a real Stripe price ID
            SubscriptionPlan.PREMIUM: "price_premium",  # This would be a real Stripe price ID
            SubscriptionPlan.ENTERPRISE: "price_enterprise"  # This would be a real Stripe price ID
        }
        
        if plan == SubscriptionPlan.FREE:
            # Free plan doesn't need Stripe, create directly in DB
            subscription = create_subscription(
                db,
                SubscriptionCreate(
                    user_id=user_id,
                    plan=SubscriptionPlan.FREE,
                    status=SubscriptionStatus.ACTIVE,
                    current_period_start=datetime.utcnow(),
                    current_period_end=datetime.utcnow() + timedelta(days=30),
                )
            )
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status.value,
                "current_period_end": subscription.current_period_end,
                "plan": subscription.plan.value
            }
        
        # Get Stripe price ID for the selected plan
        price_id = plan_to_price_id.get(plan)
        if not price_id:
            raise ValueError(f"No Stripe price defined for plan {plan}")
        
        # Check if user already has a Stripe customer ID
        # In a real implementation, you would store this in your database
        # For this example, we'll create a new customer each time
        customer = stripe.Customer.create(
            email=user.email,
            name=user.name,
            payment_method=payment_method_id,
            invoice_settings={
                "default_payment_method": payment_method_id
            }
        )
        
        # Create subscription in Stripe
        stripe_subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[
                {"price": price_id}
            ],
            expand=["latest_invoice.payment_intent"],
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            metadata={
                "user_id": user_id
            }
        )
        
        # Calculate period dates
        current_period_start = datetime.fromtimestamp(stripe_subscription.current_period_start)
        current_period_end = datetime.fromtimestamp(stripe_subscription.current_period_end)
        
        # Create subscription in database
        subscription = create_subscription(
            db,
            SubscriptionCreate(
                user_id=user_id,
                plan=plan,
                status=SubscriptionStatus(stripe_subscription.status),
                stripe_subscription_id=stripe_subscription.id,
                current_period_start=current_period_start,
                current_period_end=current_period_end,
                plan_data=json.dumps({
                    "stripe_customer_id": customer.id,
                    "price_id": price_id
                })
            )
        )
        
        # Return subscription info with client secret for payment confirmation
        return {
            "subscription_id": subscription.id,
            "stripe_subscription_id": stripe_subscription.id,
            "client_secret": stripe_subscription.latest_invoice.payment_intent.client_secret,
            "status": subscription.status.value,
            "current_period_end": current_period_end.isoformat(),
            "plan": subscription.plan.value
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise ValueError(f"Failed to create subscription: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise


def process_stripe_webhook(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process Stripe webhook events related to subscriptions.
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
        
        # Get Session to connect to database
        from app.db.session import SessionLocal
        db = SessionLocal()
        
        try:
            # Find subscription in our database
            subscription = get_subscription_by_stripe_id(db, stripe_subscription_id)
            
            if not subscription:
                logger.warning(f"Subscription not found: {stripe_subscription_id}")
                return {"status": "not_found", "subscription_id": stripe_subscription_id}
            
            # Process based on event type
            if event_type == "customer.subscription.created":
                # Already handled during creation
                pass
                
            elif event_type == "customer.subscription.updated":
                # Update subscription status
                status = SubscriptionStatus(subscription_data.get("status"))
                cancel_at_period_end = subscription_data.get("cancel_at_period_end", False)
                
                update_subscription(
                    db, 
                    subscription,
                    {
                        "status": status,
                        "cancel_at_period_end": cancel_at_period_end,
                        "current_period_start": datetime.fromtimestamp(subscription_data.get("current_period_start")),
                        "current_period_end": datetime.fromtimestamp(subscription_data.get("current_period_end")),
                    }
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
                
            return {
                "status": "processed",
                "event_type": event_type,
                "subscription_id": subscription.id
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {"status": "error", "message": str(e)}


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
            Subscription.plan,
            func.count(Subscription.id).label("count")
        )
        .group_by(Subscription.plan)
        .all()
    )
    
    plan_dict = {
        str(p.value): count for p, count in plan_counts
    }
    
    # MRR (Monthly Recurring Revenue)
    # In a real implementation, we would get the actual amounts from Stripe
    # Here we're using the hardcoded prices from get_subscription_plans()
    plan_prices = {
        SubscriptionPlan.FREE: 0,
        SubscriptionPlan.BASIC: 9.99,
        SubscriptionPlan.PREMIUM: 19.99,
        SubscriptionPlan.ENTERPRISE: 49.99
    }
    
    mrr = 0
    for plan, count in plan_counts:
        mrr += plan_prices.get(plan, 0) * count
    
    return {
        "total_subscriptions": total_subscriptions,
        "active_subscriptions": active_subscriptions,
        "by_plan": plan_dict,
        "mrr": round(mrr, 2)
    }
