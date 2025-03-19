from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.schemas.user import UserResponse


class TokenResponse(BaseModel):
    """
    Schema for token response after login/register/refresh.
    """
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """
    Schema for token refresh request.
    """
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """
    Schema for requesting a password reset.
    """
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """
    Schema for confirming a password reset.
    """
    token: str
    new_password: str


class LoginRequest(BaseModel):
    """
    Schema for JSON login request.
    """
    email: EmailStr
    password: str
