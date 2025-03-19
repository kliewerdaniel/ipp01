from pydantic import BaseModel, EmailStr, Field, UUID4, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    """
    Base schema for user data.
    """
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class OAuthUserCreate(UserBase):
    """
    Schema for creating a user via OAuth.
    """
    oauth_provider: str
    oauth_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image_url: Optional[str] = None


class UserUpdate(BaseModel):
    """
    Schema for updating user data.
    """
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """
    Schema for user response data.
    """
    id: str
    is_active: bool
    is_superuser: bool
    role: UserRole
    status: UserStatus
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    email_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserAdminResponse(UserResponse):
    """
    Extended user response for admin users.
    """
    job_title: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    years_of_experience: Optional[int] = None
    last_login: Optional[datetime] = None
    subscription_status: Optional[str] = None
    oauth_provider: Optional[str] = None


class UserProfileUpdate(BaseModel):
    """
    Schema for updating user profile data.
    """
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    years_of_experience: Optional[int] = Field(None, ge=0)
    skills: Optional[List[str]] = None
    profile_image_url: Optional[str] = None
    timezone: Optional[str] = None
    interface_language: Optional[str] = None
    email_notifications: Optional[bool] = None


class ChangePasswordRequest(BaseModel):
    """
    Schema for changing password.
    """
    current_password: str
    new_password: str = Field(..., min_length=8)


class UserPermissionResponse(BaseModel):
    """
    Schema for user permissions.
    """
    resource: str
    action: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserRoleResponse(BaseModel):
    """
    Schema for user role with associated permissions.
    """
    role: UserRole
    permissions: List[UserPermissionResponse]


class UserRoleUpdate(BaseModel):
    """
    Schema for updating a user's role.
    """
    role: UserRole

    @validator('role')
    def validate_role(cls, v):
        # Make sure the role is a valid UserRole enum value
        if v not in UserRole.__members__.values():
            raise ValueError(f'Invalid role: {v}')
        return v


class UserStatusUpdate(BaseModel):
    """
    Schema for updating a user's status.
    """
    status: UserStatus

    @validator('status')
    def validate_status(cls, v):
        # Make sure the status is a valid UserStatus enum value
        if v not in UserStatus.__members__.values():
            raise ValueError(f'Invalid status: {v}')
        return v
