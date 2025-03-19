from pydantic import BaseModel, EmailStr, AnyUrl, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.schemas.user import UserResponse


class TokenResponse(BaseModel):
    """
    Schema for token response after login/register/refresh.
    """
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse
    csrf_token: Optional[str] = None


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
    new_password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    """
    Schema for JSON login request.
    """
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False


class OAuthProvider(str, Enum):
    """
    Supported OAuth providers.
    """
    GOOGLE = "google"
    FACEBOOK = "facebook"


class OAuthRequest(BaseModel):
    """
    Schema for initiating OAuth flow.
    """
    provider: OAuthProvider
    redirect_uri: Optional[AnyUrl] = None
    state: Optional[str] = None


class OAuthCallback(BaseModel):
    """
    Schema for OAuth callback.
    """
    provider: OAuthProvider
    code: str
    state: Optional[str] = None
    error: Optional[str] = None


class EmailVerificationRequest(BaseModel):
    """
    Schema for requesting email verification.
    """
    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    """
    Schema for confirming email verification.
    """
    token: str


class UserRoleUpdate(BaseModel):
    """
    Schema for updating a user's role.
    """
    user_id: str
    role: str


class PermissionCreate(BaseModel):
    """
    Schema for creating a new permission.
    """
    name: str
    description: Optional[str] = None
    resource: str
    action: str


class PermissionResponse(BaseModel):
    """
    Schema for permission response.
    """
    id: str
    name: str
    description: Optional[str] = None
    resource: str
    action: str

    class Config:
        from_attributes = True


class UserPermissionUpdate(BaseModel):
    """
    Schema for updating a user's permissions.
    """
    user_id: str
    permissions: List[str]  # List of permission IDs


class CSRFTokenResponse(BaseModel):
    """
    Schema for CSRF token response.
    """
    csrf_token: str


class MfaSetupResponse(BaseModel):
    """
    Schema for MFA setup response.
    """
    secret_key: str
    qr_code_url: str


class MfaVerifyRequest(BaseModel):
    """
    Schema for MFA verification request.
    """
    code: str
    remember_device: Optional[bool] = False


class SessionInfo(BaseModel):
    """
    Schema for session information.
    """
    id: str
    user_agent: str
    ip_address: str
    created_at: datetime
    last_active: datetime
    is_current: bool


class DeviceInfo(BaseModel):
    """
    Schema for trusted device information.
    """
    id: str
    name: str
    trusted_until: datetime


class AuthActivityLog(BaseModel):
    """
    Schema for authentication activity log.
    """
    id: str
    user_id: str
    activity_type: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


class AccessControlPolicy(BaseModel):
    """
    Schema for access control policy.
    """
    id: str
    name: str
    description: Optional[str] = None
    resources: List[str]
    actions: List[str]
    conditions: Optional[Dict[str, Any]] = None
