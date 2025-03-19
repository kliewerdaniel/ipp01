from datetime import timedelta, datetime
import httpx
import json
import secrets
import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request, Response, Query
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    get_current_user,
    get_optional_current_user,
    set_auth_cookies,
    clear_auth_cookies,
    check_login_rate_limit,
    track_failed_login,
    reset_failed_login,
    revoke_token,
    has_role,
    has_permission,
    generate_csrf_token,
)
from app.db.session import get_db
from app.models.user import User, UserRole, UserStatus, Permission
from app.schemas.auth import (
    TokenResponse, 
    RefreshTokenRequest, 
    PasswordResetRequest, 
    PasswordResetConfirm, 
    LoginRequest,
    OAuthProvider,
    OAuthRequest,
    OAuthCallback,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    UserRoleUpdate,
    PermissionCreate,
    PermissionResponse,
    UserPermissionUpdate,
    CSRFTokenResponse,
)
from app.schemas.user import (
    UserCreate, 
    UserResponse, 
    OAuthUserCreate,
    UserAdminResponse,
    UserPermissionResponse,
    UserRoleResponse,
)
from app.services.user import get_user_by_email, create_user, get_user_by_id, update_user, get_users
from app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory storage for various tokens (in production, use Redis or DB)
password_reset_tokens: Dict[str, Dict[str, Any]] = {}
email_verification_tokens: Dict[str, Dict[str, Any]] = {}
oauth_state_tokens: Dict[str, Dict[str, Any]] = {}

router = APIRouter()

# =========== Helper Functions ===========

async def send_email_verification(
    user_email: str, 
    token: str, 
    background_tasks: BackgroundTasks,
) -> None:
    """Send an email verification email."""
    # In a real app, you'd send an email
    # For this example, just log the token
    logger.info(f"Email verification token for {user_email}: {token}")
    # Example: background_tasks.add_task(send_email, user_email, "Verify your email", f"Token: {token}")

async def send_password_reset_email(
    user_email: str, 
    token: str, 
    background_tasks: BackgroundTasks,
) -> None:
    """Send a password reset email."""
    # In a real app, you'd send an email
    # For this example, just log the token
    logger.info(f"Password reset token for {user_email}: {token}")
    # Example: background_tasks.add_task(send_email, user_email, "Reset your password", f"Token: {token}")

def get_permissions_for_user(user: User) -> List[Dict[str, str]]:
    """Get permissions for a user based on their role and direct permissions."""
    permissions = []
    
    # Add all direct permissions
    for permission in user.permissions:
        permissions.append({
            "name": permission.name,
            "resource": permission.resource,
            "action": permission.action,
            "description": permission.description
        })
    
    # Default permissions based on role
    if user.role == UserRole.ADMIN or user.role == UserRole.SUPER_ADMIN:
        # These would typically come from a role-permission mapping in the database
        admin_permissions = [
            {"name": "manage_users", "resource": "users", "action": "manage", "description": "Can manage all users"},
            {"name": "view_statistics", "resource": "statistics", "action": "read", "description": "Can view system statistics"},
        ]
        permissions.extend(admin_permissions)
    
    if user.role == UserRole.SUPER_ADMIN:
        super_admin_permissions = [
            {"name": "manage_system", "resource": "system", "action": "manage", "description": "Can manage system settings"},
            {"name": "manage_roles", "resource": "roles", "action": "manage", "description": "Can manage user roles"},
        ]
        permissions.extend(super_admin_permissions)
    
    return permissions

# =========== Authentication Endpoints ===========

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_access_token(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login with rate limiting and account lockout protection.
    """
    # Check rate limits
    if not check_login_rate_limit(request):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )
    
    user = get_user_by_email(db, email=form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is temporarily locked due to too many failed login attempts",
        )
    
    if not verify_password(form_data.password, user.hashed_password):
        # Track failed login attempt
        should_lock = track_failed_login(user.id)
        
        # Update user's failed login attempts in DB
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        user.last_failed_login = datetime.utcnow()
        
        # Lock account if necessary
        if should_lock:
            user.locked_until = datetime.utcnow() + timedelta(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
        
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Reset failed login attempts on successful login
    reset_failed_login(user.id)
    user.failed_login_attempts = 0
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    permissions = get_permissions_for_user(user)
    
    access_token = create_access_token(
        subject=user.id, 
        expires_delta=access_token_expires,
        role=user.role,
        permissions=[p["name"] for p in permissions]
    )
    refresh_token = create_refresh_token(
        subject=user.id,
        role=user.role
    )
    
    # Set secure cookies
    set_auth_cookies(response, access_token, refresh_token)
    
    # Generate CSRF token
    csrf_token = generate_csrf_token(access_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
        "csrf_token": csrf_token,
    }


@router.post("/login/json", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_json(
    login_data: LoginRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """
    JSON compatible login endpoint with rate limiting and account lockout protection.
    """
    # Check rate limits
    if not check_login_rate_limit(request):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )
    
    user = get_user_by_email(db, email=login_data.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is temporarily locked due to too many failed login attempts",
        )
    
    if not verify_password(login_data.password, user.hashed_password):
        # Track failed login attempt
        should_lock = track_failed_login(user.id)
        
        # Update user's failed login attempts in DB
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        user.last_failed_login = datetime.utcnow()
        
        # Lock account if necessary
        if should_lock:
            user.locked_until = datetime.utcnow() + timedelta(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
        
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Reset failed login attempts on successful login
    reset_failed_login(user.id)
    user.failed_login_attempts = 0
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens with appropriate expiry
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    if login_data.remember_me:
        access_token_expires = timedelta(days=7)  # Longer session for "remember me"
    
    permissions = get_permissions_for_user(user)
    
    access_token = create_access_token(
        subject=user.id, 
        expires_delta=access_token_expires,
        role=user.role,
        permissions=[p["name"] for p in permissions]
    )
    refresh_token = create_refresh_token(
        subject=user.id,
        role=user.role
    )
    
    # Set secure cookies
    set_auth_cookies(response, access_token, refresh_token)
    
    # Generate CSRF token
    csrf_token = generate_csrf_token(access_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
        "csrf_token": csrf_token,
    }


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate, 
    response: Response,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user and return tokens.
    """
    # Check if the user already exists
    existing_user = get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create the user with pending verification status
    user = create_user(db, obj_in=user_in)
    
    # Generate verification token
    token = secrets.token_urlsafe(32)
    
    # Store token with expiration
    expiration = datetime.utcnow() + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    email_verification_tokens[token] = {
        "user_id": user.id,
        "email": user.email,
        "expiration": expiration
    }
    
    # Send verification email
    await send_email_verification(user.email, token, background_tasks)
    
    # Generate tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    permissions = get_permissions_for_user(user)
    
    access_token = create_access_token(
        subject=user.id, 
        expires_delta=access_token_expires,
        role=user.role,
        permissions=[p["name"] for p in permissions]
    )
    refresh_token = create_refresh_token(
        subject=user.id,
        role=user.role
    )
    
    # Set secure cookies
    set_auth_cookies(response, access_token, refresh_token)
    
    # Generate CSRF token
    csrf_token = generate_csrf_token(access_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
        "csrf_token": csrf_token,
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using either a refresh token in request body or in cookie.
    """
    refresh_token = None
    try:
        # First try to get the token from the request body
        body = await request.json()
        refresh_token = body.get("refresh_token")
    except Exception:
        # If no body, try to get from cookie
        refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is required",
        )
    
    try:
        # Decode the refresh token
        from jose import jwt
        
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        
        # Verify this is a refresh token
        if payload.get("token_type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        
        user_id = payload.get("sub")
        jti = payload.get("jti")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        
        # Get the user
        user = get_user_by_id(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        # Create new tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        permissions = get_permissions_for_user(user)
        
        new_access_token = create_access_token(
            subject=user.id, 
            expires_delta=access_token_expires,
            role=user.role,
            permissions=[p["name"] for p in permissions]
        )
        
        new_refresh_token = create_refresh_token(
            subject=user.id,
            role=user.role
        )
        
        # Revoke the old refresh token
        if jti:
            revoke_token(refresh_token)
        
        # Set cookies
        set_auth_cookies(response, new_access_token, new_refresh_token)
        
        # Generate CSRF token
        csrf_token = generate_csrf_token(new_access_token)
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db.commit()
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user),
            "csrf_token": csrf_token,
        }
    
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    request: Request,
    token: str = Depends(get_optional_current_user)
) -> dict:
    """
    Logout endpoint - revokes tokens and clears cookies.
    """
    # Get tokens from cookies or authorization header
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    # If tokens exist, revoke them
    if access_token:
        revoke_token(access_token)
    
    if refresh_token:
        revoke_token(refresh_token)
    
    # Clear cookies
    clear_auth_cookies(response)
    
    return {"detail": "Successfully logged out"}


@router.post("/csrf-token", response_model=CSRFTokenResponse)
async def get_csrf_token(
    user = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Get a new CSRF token.
    """
    return {"csrf_token": generate_csrf_token(str(user.id))}


@router.post("/validate-token", status_code=status.HTTP_200_OK)
async def validate_token(
    user = Depends(get_current_user)
) -> dict:
    """
    Validate that the provided token is valid.
    Returns user info if token is valid.
    """
    permissions = get_permissions_for_user(user)
    
    return {
        "user_id": user.id, 
        "valid": True,
        "role": user.role,
        "permissions": permissions
    }

# =========== Password Reset Endpoints ===========

@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    request: Request = None,
) -> dict:
    """
    Request a password reset token.
    
    This endpoint will send a password reset token to the user's email.
    """
    user = get_user_by_email(db, reset_request.email)
    
    if not user:
        # Return success even if user doesn't exist to prevent user enumeration
        return {"detail": "If the email exists, a password reset link has been sent"}
    
    # Generate a secure token
    token = secrets.token_urlsafe(32)
    
    # Store token with expiration (1 hour from now)
    expiration = datetime.utcnow() + timedelta(hours=1)
    password_reset_tokens[token] = {
        "user_id": user.id,
        "expiration": expiration
    }
    
    # Send password reset email
    await send_password_reset_email(user.email, token, background_tasks)
    
    return {"detail": "If the email exists, a password reset link has been sent"}


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db)
) -> dict:
    """
    Confirm a password reset token and set a new password.
    """
    # Check if token exists and is valid
    token_data = password_reset_tokens.get(reset_confirm.token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    # Check if token is expired
    if token_data["expiration"] < datetime.utcnow():
        # Remove expired token
        password_reset_tokens.pop(reset_confirm.token)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired"
        )
    
    # Get user
    user = get_user_by_id(db, token_data["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user's password
    update_user(
        db,
        db_obj=user,
        obj_in={"password": reset_confirm.new_password}
    )
    
    # Reset failed login attempts
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    
    # Remove used token
    password_reset_tokens.pop(reset_confirm.token)
    
    return {"detail": "Password has been reset successfully"}

# =========== Email Verification Endpoints ===========

@router.post("/email/verify/request", status_code=status.HTTP_202_ACCEPTED)
async def request_email_verification(
    verification_request: EmailVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> dict:
    """
    Request an email verification token.
    
    This endpoint will send a verification token to the user's email.
    """
    user = get_user_by_email(db, verification_request.email)
    
    if not user:
        # Return success even if user doesn't exist to prevent user enumeration
        return {"detail": "If the email exists, a verification link has been sent"}
    
    if user.email_verified:
        return {"detail": "Email is already verified"}
    
    # Generate a secure token
    token = secrets.token_urlsafe(32)
    
    # Store token with expiration
    expiration = datetime.utcnow() + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    email_verification_tokens[token] = {
        "user_id": user.id,
        "email": user.email,
        "expiration": expiration
    }
    
    # Send verification email
    await send_email_verification(user.email, token, background_tasks)
    
    return {"detail": "If the email exists, a verification link has been sent"}


@router.post("/email/verify/confirm", status_code=status.HTTP_200_OK)
async def confirm_email_verification(
    verification_confirm: EmailVerificationConfirm,
    db: Session = Depends(get_db)
) -> dict:
    """
    Confirm an email verification token.
    """
    # Check if token exists and is valid
    token_data = email_verification_tokens.get(verification_confirm.token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    # Check if token is expired
    if token_data["expiration"] < datetime.utcnow():
        # Remove expired token
        email_verification_tokens.pop(verification_confirm.token)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired"
        )
    
    # Get user
    user = get_user_by_id(db, token_data["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Mark email as verified
    user.email_verified = True
    user.email_verified_at = datetime.utcnow()
    user.status = UserStatus.ACTIVE  # Update status from pending_verification to active
    db.commit()
    
    # Remove used token
    email_verification_tokens.pop(verification_confirm.token)
    
    return {"detail": "Email has been verified successfully"}

# =========== OAuth Endpoints ===========

@router.get("/oauth/{provider}", status_code=status.HTTP_302_FOUND)
async def oauth_login(
    provider: OAuthProvider,
    redirect_uri: Optional[str] = Query(None),
    request: Request = None
) -> RedirectResponse:
    """
    Initiate OAuth login flow.
    Redirects the user to the provider's authorization URL.
    """
    # Check if provider is supported
    if provider not in settings.OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )
    
    # Get provider config
    provider_config = settings.OAUTH_PROVIDERS[provider]
    
    # Generate state token to prevent CSRF
    state = secrets.token_urlsafe(32)
    
    # Store state with redirect URI for callback
    oauth_state_tokens[state] = {
        "provider": provider,
        "redirect_uri": redirect_uri,
        "created_at": datetime.utcnow()
    }
    
    # Construct the authorization URL
    if provider == OAuthProvider.GOOGLE:
        # For Google, use the discovery URL to get the auth URL
        # In a real app, you'd fetch this dynamically from the discovery URL
        auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    else:
        auth_url = provider_config["auth_url"]
    
    # Construct query parameters
    params = {
        "client_id": provider_config["client_id"],
        "redirect_uri": provider_config["redirect_uri"],
        "response_type": "code",
        "scope": "openid email profile" if provider == OAuthProvider.GOOGLE else "email",
        "state": state
    }
    
    # Redirect to authorization URL
    return RedirectResponse(f"{auth_url}?{urlencode(params)}")


@router.get("/oauth/{provider}/callback", response_model=TokenResponse)
async def oauth_callback(
    provider: OAuthProvider,
    code: str,
    state: str,
    response: Response,
    db: Session = Depends(get_db)
) -> Union[RedirectResponse, TokenResponse]:
    """
    Handle OAuth callback.
    Exchanges the code for an access token and creates/authenticates the user.
    """
    # Verify state token to prevent CSRF
    state_data = oauth_state_tokens.get(state)
    if not state_data or state_data["provider"] != provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state token"
        )
    
    # Check if provider is supported
    if provider not in settings.OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )
    
    # Get provider config
    provider_config = settings.OAUTH_PROVIDERS[provider]
    
    try:
        # Exchange code for token
        if provider == OAuthProvider.GOOGLE:
            token_url = "https://oauth2.googleapis.com/token"
        else:
            token_url = provider_config["token_url"]
        
        token_data = {
            "client_id": provider_config["client_id"],
            "client_secret": provider_config["client_secret"],
            "code": code,
            "redirect_uri": provider_config["redirect_uri"],
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()
            token_info = token_response.json()
        
        # Get user info from provider
        if provider == OAuthProvider.GOOGLE:
            user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            headers = {"Authorization": f"Bearer {token_info['access_token']}"}
            
            async with httpx.AsyncClient() as client:
                user_response = await client.get(user_info_url, headers=headers)
                user_response.raise_for_status()
                user_info = user_response.json()
            
            # Extract user data from Google response
            email = user_info.get("email")
            name = user_info.get("name")
            first_name = user_info.get("given_name")
            last_name = user_info.get("family_name")
            profile_image_url = user_info.get("picture")
            oauth_id = user_info.get("sub")
            email_verified = user_info.get("email_verified", False)
            
        elif provider == OAuthProvider.FACEBOOK:
            user_info_url = provider_config["user_info_url"]
            headers = {"Authorization": f"Bearer {token_info['access_token']}"}
            
            async with httpx.AsyncClient() as client:
                user_response = await client.get(user_info_url, headers=headers)
                user_response.raise_for_status()
                user_info = user_response.json()
            
            # Extract user data from Facebook response
            email = user_info.get("email")
            name = user_info.get("name")
            profile_image_url = user_info.get("picture", {}).get("data", {}).get("url")
            oauth_id = user_info.get("id")
            email_verified = True  # Facebook provides verified emails
            first_name = None
            last_name = None
            
            # Try to split name into first and last name
            if name:
                parts = name.split(" ", 1)
                if len(parts) > 0:
                    first_name = parts[0]
                if len(parts) > 1:
                    last_name = parts[1]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}"
            )
        
        # Ensure we have an email
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by OAuth provider"
            )
        
        # Check if user exists
        user = get_user_by_email(db, email=email)
        
        if not user:
            # Create new user
            user_data = OAuthUserCreate(
                email=email,
                name=name,
                oauth_provider=provider,
                oauth_id=oauth_id,
                first_name=first_name,
                last_name=last_name,
                profile_image_url=profile_image_url
            )
            
            user = create_user(db, obj_in=user_data, oauth=True)
            
            # Mark email as verified if provider verified it
            if email_verified:
                user.email_verified = True
                user.email_verified_at = datetime.utcnow()
                user.status = UserStatus.ACTIVE
                db.commit()
        else:
            # Update existing user's OAuth info if needed
            if not user.oauth_provider or not user.oauth_id:
                user.oauth_provider = provider
                user.oauth_id = oauth_id
                
                # Update profile info if missing
                if not user.profile_image_url and profile_image_url:
                    user.profile_image_url = profile_image_url
                if not user.first_name and first_name:
                    user.first_name = first_name
                if not user.last_name and last_name:
                    user.last_name = last_name
                
                db.commit()
        
        # Generate tokens for authentication
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        permissions = get_permissions_for_user(user)
        
        access_token = create_access_token(
            subject=user.id, 
            expires_delta=access_token_expires,
            role=user.role,
            permissions=[p["name"] for p in permissions]
        )
        refresh_token = create_refresh_token(
            subject=user.id,
            role=user.role
        )
        
        # Set secure cookies
        set_auth_cookies(response, access_token, refresh_token)
        
        # Generate CSRF token
        csrf_token = generate_csrf_token(access_token)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Check if we need to redirect
        redirect_uri = state_data.get("redirect_uri")
        if redirect_uri:
            return RedirectResponse(redirect_uri)
        
        # Otherwise return token response
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user),
            "csrf_token": csrf_token,
        }
        
    except Exception as e:
        logger.error(f"OAuth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth authentication failed: {str(e)}"
        )
