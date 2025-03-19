from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional
from datetime import datetime

from app.models.user import UserRole, UserStatus
from app.schemas.user import UserResponse


class CloneRequest(BaseModel):
    """
    Schema for creating a new platform clone.
    """
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50, pattern="^[a-z0-9-]+$")
    primary_color: str = Field(default="#007bff", pattern="^#[0-9a-fA-F]{6}$")
    secondary_color: str = Field(default="#6c757d", pattern="^#[0-9a-fA-F]{6}$")
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    domain: Optional[str] = None


class CloneResponse(BaseModel):
    """
    Schema for clone response.
    """
    id: str
    name: str
    slug: str
    primary_color: str
    secondary_color: str
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    domain: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AdminDashboardStats(BaseModel):
    """
    Schema for admin dashboard statistics.
    """
    total_users: int
    active_users: int
    new_users_last_30_days: int
    total_interviews: int
    interviews_last_30_days: int
    avg_interviews_per_user: float
    common_questions: List[Dict[str, any]]
    platform_usage: Dict[str, any]
    subscription_stats: Dict[str, any]


class AdminUserManagement(BaseModel):
    """
    Schema for admin user management.
    """
    users: List[UserResponse]
    total_count: int


class AdminUserCreate(BaseModel):
    """
    Schema for admin to create a user.
    """
    email: EmailStr
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: str = Field(..., min_length=8)
    is_superuser: bool = False
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    email_verified: bool = False


class AdminUserUpdate(BaseModel):
    """
    Schema for admin to update a user.
    """
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    profile_image_url: Optional[str] = None
    subscription_status: Optional[str] = None
    email_verified: Optional[bool] = None
