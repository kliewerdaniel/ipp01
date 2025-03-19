from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.schemas.user import UserResponse


class CloneRequest(BaseModel):
    """
    Schema for requesting a platform clone.
    """
    name: str
    domain: str
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8)


class CloneResponse(BaseModel):
    """
    Schema for platform clone response.
    """
    id: str
    name: str
    domain: str
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    admin_id: str
    created_at: datetime


class UserStatistics(BaseModel):
    """
    Schema for user statistics.
    """
    total_users: int
    active_users: int
    premium_users: int
    new_users_last_30_days: int
    user_growth_rate: float  # Percentage


class SubscriptionStatistics(BaseModel):
    """
    Schema for subscription statistics.
    """
    total_subscriptions: int
    active_subscriptions: int
    by_plan: Dict[str, int]
    churn_rate: float  # Percentage
    mrr: float  # Monthly Recurring Revenue


class UserActivityStatistics(BaseModel):
    """
    Schema for user activity statistics.
    """
    total_interviews: int
    total_answers: int
    avg_answers_per_user: float
    avg_feedback_score: float
    interviews_last_30_days: int


class AdminDashboardStats(BaseModel):
    """
    Schema for admin dashboard statistics.
    """
    user_stats: UserStatistics
    subscription_stats: SubscriptionStatistics
    activity_stats: UserActivityStatistics
    revenue_last_30_days: float
    active_clones: int


class AdminUserManagement(BaseModel):
    """
    Schema for admin user management operations.
    """
    users: List[UserResponse]
    total_count: int


class AdminUserCreate(BaseModel):
    """
    Schema for admin creating a new user.
    """
    email: EmailStr
    name: str
    password: str = Field(..., min_length=8)
    is_superuser: bool = False


class AdminUserUpdate(BaseModel):
    """
    Schema for admin updating a user.
    """
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
