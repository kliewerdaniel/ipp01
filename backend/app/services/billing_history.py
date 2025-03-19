from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.billing_history import BillingHistory, BillingEventType
from app.schemas.subscription import BillingHistoryResponse


def get_billing_history_by_id(db: Session, id: str) -> Optional[BillingHistory]:
    """
    Get a billing history record by ID.
    """
    return db.query(BillingHistory).filter(BillingHistory.id == id).first()


def get_user_billing_history(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[BillingEventType] = None,
    visible_only: bool = True
) -> List[BillingHistory]:
    """
    Get billing history for a user with optional filtering.
    """
    query = (
        db.query(BillingHistory)
        .filter(BillingHistory.user_id == user_id)
    )
    
    # Apply filters
    if event_type:
        query = query.filter(BillingHistory.event_type == event_type)
    
    if visible_only:
        query = query.filter(BillingHistory.is_visible_to_customer == True)
    
    # Order by event time descending (newest first)
    query = query.order_by(desc(BillingHistory.event_time))
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()


def get_subscription_billing_history(
    db: Session,
    subscription_id: str,
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[BillingEventType] = None,
    visible_only: bool = True
) -> List[BillingHistory]:
    """
    Get billing history for a specific subscription with optional filtering.
    """
    query = (
        db.query(BillingHistory)
        .filter(BillingHistory.subscription_id == subscription_id)
    )
    
    # Apply filters
    if event_type:
        query = query.filter(BillingHistory.event_type == event_type)
    
    if visible_only:
        query = query.filter(BillingHistory.is_visible_to_customer == True)
    
    # Order by event time descending (newest first)
    query = query.order_by(desc(BillingHistory.event_time))
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()


def search_billing_history(
    db: Session,
    search_term: str,
    skip: int = 0,
    limit: int = 100
) -> List[BillingHistory]:
    """
    Search billing history records for admin purposes.
    """
    query = (
        db.query(BillingHistory)
        .filter(
            BillingHistory.description.ilike(f"%{search_term}%") |
            BillingHistory.invoice_id.ilike(f"%{search_term}%") |
            BillingHistory.stripe_event_id.ilike(f"%{search_term}%") |
            BillingHistory.stripe_invoice_id.ilike(f"%{search_term}%") |
            BillingHistory.stripe_payment_intent_id.ilike(f"%{search_term}%")
        )
    )
    
    # Order by event time descending (newest first)
    query = query.order_by(desc(BillingHistory.event_time))
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()


def get_billing_statistics(db: Session) -> Dict[str, Any]:
    """
    Get statistics on billing events for administrative purposes.
    """
    # Total billing events
    total_events = db.query(BillingHistory).count()
    
    # Events by type
    events_by_type = (
        db.query(
            BillingHistory.event_type,
            db.func.count(BillingHistory.id).label("count")
        )
        .group_by(BillingHistory.event_type)
        .all()
    )
    
    event_type_dict = {
        event_type.value: count for event_type, count in events_by_type
    }
    
    # Success vs. failed payments
    payment_events = (
        db.query(
            BillingHistory.payment_status,
            db.func.count(BillingHistory.id).label("count")
        )
        .filter(BillingHistory.payment_status.isnot(None))
        .group_by(BillingHistory.payment_status)
        .all()
    )
    
    payment_status_dict = {
        status.value: count for status, count in payment_events
    }
    
    # Recent activity (last 30 days count)
    recent_count = (
        db.query(db.func.count(BillingHistory.id))
        .filter(
            BillingHistory.event_time >= db.func.current_timestamp() - db.func.interval('30 days')
        )
        .scalar() or 0
    )
    
    return {
        "total_events": total_events,
        "by_event_type": event_type_dict,
        "by_payment_status": payment_status_dict,
        "recent_activity_count": recent_count
    }
