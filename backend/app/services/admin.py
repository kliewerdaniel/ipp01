from typing import Optional, List, Dict, Any, Union, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import logging
from datetime import datetime, timedelta

from app.models.user import User
from app.models.subscription import Subscription, SubscriptionStatus, SubscriptionPlan
from app.models.payment import Payment, PaymentStatus
from app.models.interview import Interview
from app.models.answer import Answer
from app.schemas.admin import (
    CloneRequest,
    CloneResponse,
    AdminUserUpdate,
    UserStatistics,
    SubscriptionStatistics,
    UserActivityStatistics,
    AdminDashboardStats
)
from app.core.security import get_password_hash
from app.services.user import create_user
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


def get_admin_dashboard_stats(db: Session) -> AdminDashboardStats:
    """
    Get comprehensive statistics for the admin dashboard.
    """
    # Get user statistics
    user_stats = get_user_statistics(db)
    
    # Get subscription statistics
    subscription_stats = get_subscription_statistics(db)
    
    # Get user activity statistics
    activity_stats = get_user_activity_statistics(db)
    
    # Get revenue for last 30 days
    revenue_last_30_days = get_revenue_last_30_days(db)
    
    # For a real implementation, this would count actual platform clones
    # For now, we'll just return a placeholder
    active_clones = 1
    
    return AdminDashboardStats(
        user_stats=user_stats,
        subscription_stats=subscription_stats,
        activity_stats=activity_stats,
        revenue_last_30_days=revenue_last_30_days,
        active_clones=active_clones
    )


def get_user_statistics(db: Session) -> UserStatistics:
    """
    Get user statistics for the admin dashboard.
    """
    # Total users
    total_users = db.query(func.count(User.id)).scalar() or 0
    
    # Active users
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    
    # Premium users (users with active premium/enterprise subscriptions)
    premium_users = (
        db.query(func.count(User.id))
        .join(Subscription, User.id == Subscription.user_id)
        .filter(
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.plan.in_([SubscriptionPlan.PREMIUM, SubscriptionPlan.ENTERPRISE])
        )
        .scalar() or 0
    )
    
    # New users in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users_last_30_days = (
        db.query(func.count(User.id))
        .filter(User.created_at >= thirty_days_ago)
        .scalar() or 0
    )
    
    # User growth rate (comparing last 30 days to previous 30 days)
    sixty_days_ago = datetime.utcnow() - timedelta(days=60)
    users_30_60_days_ago = (
        db.query(func.count(User.id))
        .filter(User.created_at >= sixty_days_ago, User.created_at < thirty_days_ago)
        .scalar() or 0
    )
    
    # Calculate growth rate
    if users_30_60_days_ago > 0:
        user_growth_rate = ((new_users_last_30_days - users_30_60_days_ago) / users_30_60_days_ago) * 100
    else:
        user_growth_rate = 0 if new_users_last_30_days == 0 else 100
    
    return UserStatistics(
        total_users=total_users,
        active_users=active_users,
        premium_users=premium_users,
        new_users_last_30_days=new_users_last_30_days,
        user_growth_rate=round(user_growth_rate, 2)
    )


def get_subscription_statistics(db: Session) -> SubscriptionStatistics:
    """
    Get subscription statistics for the admin dashboard.
    """
    # Total subscriptions
    total_subscriptions = db.query(func.count(Subscription.id)).scalar() or 0
    
    # Active subscriptions
    active_subscriptions = (
        db.query(func.count(Subscription.id))
        .filter(Subscription.status == SubscriptionStatus.ACTIVE)
        .scalar() or 0
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
    
    by_plan = {
        str(p.value): count for p, count in plan_counts
    }
    
    # Calculate churn rate (canceled subscriptions / total subscriptions)
    # In a real implementation, this would be more sophisticated
    # and look at specific time periods
    canceled_subscriptions = (
        db.query(func.count(Subscription.id))
        .filter(
            Subscription.status == SubscriptionStatus.CANCELED,
            Subscription.canceled_at >= (datetime.utcnow() - timedelta(days=30))
        )
        .scalar() or 0
    )
    
    subscriptions_30_days_ago = (
        db.query(func.count(Subscription.id))
        .filter(Subscription.created_at <= (datetime.utcnow() - timedelta(days=30)))
        .scalar() or 0
    )
    
    if subscriptions_30_days_ago > 0:
        churn_rate = (canceled_subscriptions / subscriptions_30_days_ago) * 100
    else:
        churn_rate = 0
    
    # Calculate MRR (Monthly Recurring Revenue)
    # In a real implementation, we'd get this from Stripe
    # or calculate it based on actual subscription amounts
    # Here we'll use some placeholder values for each plan
    plan_prices = {
        SubscriptionPlan.FREE: 0,
        SubscriptionPlan.BASIC: 9.99,
        SubscriptionPlan.PREMIUM: 19.99,
        SubscriptionPlan.ENTERPRISE: 49.99
    }
    
    mrr = 0
    for plan, count in plan_counts:
        if plan in plan_prices and Subscription.status == SubscriptionStatus.ACTIVE:
            mrr += plan_prices[plan] * count
    
    return SubscriptionStatistics(
        total_subscriptions=total_subscriptions,
        active_subscriptions=active_subscriptions,
        by_plan=by_plan,
        churn_rate=round(churn_rate, 2),
        mrr=round(mrr, 2)
    )


def get_user_activity_statistics(db: Session) -> UserActivityStatistics:
    """
    Get user activity statistics for the admin dashboard.
    """
    # Total interviews
    total_interviews = db.query(func.count(Interview.id)).scalar() or 0
    
    # Total answers
    total_answers = db.query(func.count(Answer.id)).scalar() or 0
    
    # Average answers per user
    total_users = db.query(func.count(User.id)).scalar() or 0
    avg_answers_per_user = total_answers / total_users if total_users > 0 else 0
    
    # Average feedback score
    avg_feedback_score = (
        db.query(func.avg(Answer.feedback_score))
        .filter(Answer.feedback_score.isnot(None))
        .scalar() or 0
    )
    
    # Interviews in last 30 days
    interviews_last_30_days = (
        db.query(func.count(Interview.id))
        .filter(Interview.created_at >= (datetime.utcnow() - timedelta(days=30)))
        .scalar() or 0
    )
    
    return UserActivityStatistics(
        total_interviews=total_interviews,
        total_answers=total_answers,
        avg_answers_per_user=round(avg_answers_per_user, 2),
        avg_feedback_score=round(avg_feedback_score, 2),
        interviews_last_30_days=interviews_last_30_days
    )


def get_revenue_last_30_days(db: Session) -> float:
    """
    Get total revenue for the last 30 days.
    """
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    revenue = (
        db.query(func.sum(Payment.amount))
        .filter(
            Payment.status == PaymentStatus.SUCCEEDED,
            Payment.created_at >= thirty_days_ago
        )
        .scalar() or 0
    )
    
    return float(revenue)


def create_platform_clone(db: Session, clone_request: CloneRequest) -> CloneResponse:
    """
    Create a new platform clone with admin user.
    
    In a real implementation, this would:
    1. Set up a new database schema or tenant
    2. Configure custom branding
    3. Create DNS entries
    4. Set up cloud infrastructure
    
    For this example, we'll just create an admin user and return a simulated response.
    """
    # Create admin user
    admin_user = create_user(
        db, 
        UserCreate(
            email=clone_request.admin_email,
            password=clone_request.admin_password,
            name="Admin"
        )
    )
    
    # Update user to be a superuser
    admin_user.is_superuser = True
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    # Simulate clone creation
    # In a real implementation, this would create actual infrastructure
    logger.info(f"Created platform clone {clone_request.name} at {clone_request.domain}")
    
    # Return clone details
    return CloneResponse(
        id=f"clone_{admin_user.id}",
        name=clone_request.name,
        domain=clone_request.domain,
        logo_url=clone_request.logo_url,
        primary_color=clone_request.primary_color,
        secondary_color=clone_request.secondary_color,
        admin_id=admin_user.id,
        created_at=datetime.utcnow()
    )


def get_admin_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None
) -> Tuple[List[User], int]:
    """
    Get users with pagination and optional search for admin panel.
    Returns a tuple of (users, total_count).
    """
    query = db.query(User)
    
    if search:
        search = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search)) | 
            (User.name.ilike(search))
        )
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply pagination and get users
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    return users, total_count


def admin_update_user(
    db: Session, 
    user_id: str, 
    user_update: AdminUserUpdate
) -> User:
    """
    Admin update of a user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User with ID {user_id} not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Hash password if it's being updated
    if "password" in update_data and update_data["password"]:
        user.hashed_password = get_password_hash(update_data.pop("password"))
    
    # Update other fields
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"Admin updated user: {user.email}")
    return user


def admin_create_user(db: Session, user_data: UserCreate, is_superuser: bool = False) -> User:
    """
    Admin creation of a user.
    """
    # Create user
    user = create_user(db, user_data)
    
    # If this should be a superuser, update that flag
    if is_superuser:
        user.is_superuser = True
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created superuser: {user.email}")
    
    return user
