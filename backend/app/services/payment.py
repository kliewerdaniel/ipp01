from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import logging
import stripe
import json
from datetime import datetime

from app.models.payment import Payment, PaymentStatus, PaymentType
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentIntentResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Stripe client
if settings.STRIPE_API_KEY:
    stripe.api_key = settings.STRIPE_API_KEY
else:
    logger.warning("Stripe API key not configured. Stripe functionality will be limited.")


def get_payment_by_id(db: Session, id: str) -> Optional[Payment]:
    """
    Get a payment by ID.
    """
    return db.query(Payment).filter(Payment.id == id).first()


def get_payment_by_stripe_id(db: Session, stripe_id: str) -> Optional[Payment]:
    """
    Get a payment by Stripe payment ID.
    """
    return db.query(Payment).filter(Payment.stripe_payment_id == stripe_id).first()


def get_user_payments(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    payment_type: Optional[PaymentType] = None,
    status: Optional[PaymentStatus] = None,
) -> List[Payment]:
    """
    Get payments for a user with optional filtering.
    """
    query = db.query(Payment).filter(Payment.user_id == user_id)
    
    if payment_type:
        query = query.filter(Payment.payment_type == payment_type)
    
    if status:
        query = query.filter(Payment.status == status)
    
    # Order by creation date, newest first
    query = query.order_by(desc(Payment.created_at))
    
    return query.offset(skip).limit(limit).all()


def create_payment(db: Session, obj_in: PaymentCreate) -> Payment:
    """
    Create a new payment record.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == obj_in.user_id).first()
    if not user:
        raise ValueError(f"User with ID {obj_in.user_id} not found")
    
    # Create payment record
    db_obj = Payment(
        user_id=obj_in.user_id,
        stripe_payment_id=obj_in.stripe_payment_id,
        amount=obj_in.amount,
        currency=obj_in.currency,
        status=obj_in.status,
        payment_type=obj_in.payment_type,
        description=obj_in.description,
        payment_method=obj_in.payment_method,
        receipt_url=obj_in.receipt_url,
        payment_metadata=obj_in.payment_metadata,
    )
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    logger.info(f"Created new payment: {db_obj.id} for user {db_obj.user_id}")
    return db_obj


def update_payment(
    db: Session, 
    db_obj: Payment, 
    obj_in: Union[PaymentUpdate, Dict[str, Any]]
) -> Payment:
    """
    Update a payment record.
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    # Update payment with new data
    for field in update_data:
        if hasattr(db_obj, field):
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    logger.info(f"Updated payment: {db_obj.id}")
    return db_obj


def create_payment_intent(
    user_id: str,
    amount: float,
    currency: str = "usd",
    payment_type: PaymentType = PaymentType.ONE_TIME,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> PaymentIntentResponse:
    """
    Create a payment intent in Stripe.
    """
    if not settings.STRIPE_API_KEY:
        raise ValueError("Stripe API key not configured")
    
    try:
        # Convert amount to cents/smallest currency unit
        amount_int = int(amount * 100)
        
        # Create the payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount_int,
            currency=currency,
            description=description,
            metadata={
                "user_id": user_id,
                "payment_type": payment_type.value,
                **(metadata or {})
            }
        )
        
        return PaymentIntentResponse(
            client_secret=intent.client_secret,
            payment_intent_id=intent.id,
            amount=amount,
            currency=currency,
            status=intent.status
        )
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise ValueError(f"Failed to create payment intent: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
        raise


def get_payment_methods(user_id: str, stripe_customer_id: str) -> List[Dict[str, Any]]:
    """
    Get saved payment methods for a user from Stripe.
    """
    if not settings.STRIPE_API_KEY:
        raise ValueError("Stripe API key not configured")
    
    try:
        # Get payment methods from Stripe
        payment_methods = stripe.PaymentMethod.list(
            customer=stripe_customer_id,
            type="card"
        )
        
        # Format the payment methods
        formatted_methods = []
        for pm in payment_methods.data:
            card = pm.card
            formatted_methods.append({
                "id": pm.id,
                "type": pm.type,
                "card": {
                    "brand": card.brand,
                    "last4": card.last4,
                    "exp_month": card.exp_month,
                    "exp_year": card.exp_year,
                },
                "billing_details": pm.billing_details,
                "created": datetime.fromtimestamp(pm.created)
            })
        
        return formatted_methods
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise ValueError(f"Failed to get payment methods: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting payment methods: {str(e)}")
        raise


def process_payment_webhook(db: Session, event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process Stripe webhook events related to payments.
    """
    event_type = event_data.get("type")
    
    # Return early if this is not a payment-related event
    if not (event_type.startswith("payment_intent") or event_type.startswith("charge")):
        return {"status": "ignored", "event_type": event_type}
    
    try:
        # Get payment data from the event
        if event_type.startswith("payment_intent"):
            payment_data = event_data.get("data", {}).get("object", {})
            stripe_payment_id = payment_data.get("id")
            payment_status_mapping = {
                "succeeded": PaymentStatus.SUCCEEDED,
                "processing": PaymentStatus.PENDING,
                "requires_payment_method": PaymentStatus.FAILED,
                "requires_action": PaymentStatus.PENDING,
                "canceled": PaymentStatus.FAILED,
            }
        elif event_type.startswith("charge"):
            payment_data = event_data.get("data", {}).get("object", {})
            stripe_payment_id = payment_data.get("payment_intent")
            payment_status_mapping = {
                "succeeded": PaymentStatus.SUCCEEDED,
                "failed": PaymentStatus.FAILED,
                "pending": PaymentStatus.PENDING,
                "refunded": PaymentStatus.REFUNDED,
                "partially_refunded": PaymentStatus.PARTIALLY_REFUNDED,
            }
        else:
            return {"status": "ignored", "event_type": event_type}
        
        if not stripe_payment_id:
            logger.error("No payment ID in webhook event")
            return {"status": "error", "message": "No payment ID in event"}
        
        # Find payment in our database
        payment = get_payment_by_stripe_id(db, stripe_payment_id)
        
        # If payment doesn't exist and this is a successful charge, create it
        if not payment and event_type == "charge.succeeded":
            # Extract user ID from metadata
            metadata = payment_data.get("metadata", {})
            user_id = metadata.get("user_id")
            
            if not user_id:
                logger.error("No user ID in payment metadata")
                return {"status": "error", "message": "No user ID in payment metadata"}
            
            # Create new payment record
            payment_type_value = metadata.get("payment_type", PaymentType.ONE_TIME.value)
            try:
                payment_type = PaymentType(payment_type_value)
            except ValueError:
                payment_type = PaymentType.ONE_TIME
            
            payment = create_payment(
                db,
                PaymentCreate(
                    user_id=user_id,
                    stripe_payment_id=stripe_payment_id,
                    amount=payment_data.get("amount") / 100,  # Convert from cents
                    currency=payment_data.get("currency", "usd"),
                    status=PaymentStatus.SUCCEEDED,
                    payment_type=payment_type,
                    description=payment_data.get("description"),
                    payment_method=payment_data.get("payment_method_details", {}).get("type"),
                    receipt_url=payment_data.get("receipt_url"),
                    payment_metadata=json.dumps(metadata)
                )
            )
            
            return {
                "status": "created",
                "event_type": event_type,
                "payment_id": payment.id
            }
        
        # If payment exists, update its status
        if payment:
            stripe_status = payment_data.get("status")
            if stripe_status in payment_status_mapping:
                status = payment_status_mapping[stripe_status]
                
                # Update payment status
                update_payment(
                    db,
                    payment,
                    {"status": status}
                )
                
                return {
                    "status": "updated",
                    "event_type": event_type,
                    "payment_id": payment.id,
                    "new_status": status.value
                }
        
        return {"status": "no_action", "event_type": event_type}
        
    except Exception as e:
        logger.error(f"Error processing payment webhook: {str(e)}")
        return {"status": "error", "message": str(e)}


def get_payment_statistics(db: Session) -> Dict[str, Any]:
    """
    Get statistics on payments.
    """
    # Total payments amount
    total_amount = (
        db.query(func.sum(Payment.amount))
        .filter(Payment.status == PaymentStatus.SUCCEEDED)
        .scalar() or 0
    )
    
    # Total payments count
    total_count = (
        db.query(func.count(Payment.id))
        .filter(Payment.status == PaymentStatus.SUCCEEDED)
        .scalar() or 0
    )
    
    # Payments by type
    type_counts = (
        db.query(
            Payment.payment_type,
            func.count(Payment.id).label("count"),
            func.sum(Payment.amount).label("amount")
        )
        .filter(Payment.status == PaymentStatus.SUCCEEDED)
        .group_by(Payment.payment_type)
        .all()
    )
    
    type_stats = {
        str(t.value): {
            "count": count,
            "amount": float(amount) if amount else 0
        } for t, count, amount in type_counts
    }
    
    # Payments by month (last 6 months)
    current_date = datetime.utcnow()
    month_stats = []
    
    for i in range(5, -1, -1):
        month = (current_date.month - i) % 12 or 12
        year = current_date.year - ((current_date.month - i - 1) // 12)
        
        amount = (
            db.query(func.sum(Payment.amount))
            .filter(
                Payment.status == PaymentStatus.SUCCEEDED,
                func.extract('month', Payment.created_at) == month,
                func.extract('year', Payment.created_at) == year
            )
            .scalar() or 0
        )
        
        count = (
            db.query(func.count(Payment.id))
            .filter(
                Payment.status == PaymentStatus.SUCCEEDED,
                func.extract('month', Payment.created_at) == month,
                func.extract('year', Payment.created_at) == year
            )
            .scalar() or 0
        )
        
        month_stats.append({
            "month": month,
            "year": year,
            "amount": float(amount),
            "count": count
        })
    
    return {
        "total_amount": float(total_amount),
        "total_count": total_count,
        "by_type": type_stats,
        "monthly_stats": month_stats
    }
