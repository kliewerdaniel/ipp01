from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any, Dict
import secrets
import logging

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    get_current_user,
)
from app.db.session import get_db
from app.schemas.auth import TokenResponse, RefreshTokenRequest, PasswordResetRequest, PasswordResetConfirm, LoginRequest
from app.schemas.user import UserCreate, UserResponse
from app.services.user import get_user_by_email, create_user, get_user_by_id, update_user
from app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory storage for password reset tokens (in a real app, this would be in a database)
password_reset_tokens: Dict[str, Dict[str, Any]] = {}

router = APIRouter()


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = get_user_by_email(db, email=form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "access_token": create_access_token(user.id, expires_delta=access_token_expires),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }


@router.post("/login/json", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_json(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    JSON compatible login endpoint, get an access token for future requests.
    """
    user = get_user_by_email(db, email=login_data.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "access_token": create_access_token(user.id, expires_delta=access_token_expires),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
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
    
    # Create the user
    user = create_user(db, obj_in=user_in)
    
    # Generate tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "access_token": create_access_token(user.id, expires_delta=access_token_expires),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token_data: RefreshTokenRequest, db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token.
    """
    try:
        from jose import jwt
        
        # Decode the refresh token
        payload = jwt.decode(
            refresh_token_data.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
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
        
        return {
            "access_token": create_access_token(user.id, expires_delta=access_token_expires),
            "refresh_token": create_refresh_token(user.id),
            "token_type": "bearer",
            "user": UserResponse.model_validate(user),
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate refresh token: {str(e)}",
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout() -> dict:
    """
    Logout endpoint - client side should remove tokens.
    
    This is just a dummy endpoint as token invalidation is handled client-side.
    In a more advanced implementation, you might want to add the token to a blocklist.
    """
    return {"detail": "Successfully logged out"}


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
    
    # In a real app, you would send an email here
    # For this example, we'll log the token
    logger.info(f"Password reset token for {user.email}: {token}")
    
    # Simulate sending an email in the background
    # background_tasks.add_task(send_password_reset_email, user.email, token)
    
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
    
    # Remove used token
    password_reset_tokens.pop(reset_confirm.token)
    
    return {"detail": "Password has been reset successfully"}


@router.post("/validate-token", status_code=status.HTTP_200_OK)
async def validate_token(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Validate that the provided token is valid.
    Returns user ID if token is valid.
    """
    return {"user_id": current_user["id"], "valid": True}
