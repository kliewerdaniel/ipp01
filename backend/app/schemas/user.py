from pydantic import BaseModel, EmailStr, Field, UUID4
from typing import Optional, List
from datetime import datetime


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


class UserUpdate(BaseModel):
    """
    Schema for updating user data.
    """
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    """
    Schema for user response data.
    """
    id: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """
    Schema for updating user profile data.
    """
    name: Optional[str] = None
    bio: Optional[str] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    years_of_experience: Optional[int] = Field(None, ge=0)
    skills: Optional[List[str]] = None
    profile_picture_url: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """
    Schema for changing password.
    """
    current_password: str
    new_password: str = Field(..., min_length=8)
