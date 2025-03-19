from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
)
from app.db.session import get_db
from app.schemas.auth import TokenResponse, RefreshTokenRequest
from app.schemas.user import UserCreate, UserResponse
from app.services.user import get_user_by_email, create_user, get_user_by_id
from app.core.config import settings

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
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


@router.post("/register", response_model=TokenResponse)
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


@router.post("/logout")
async def logout() -> dict:
    """
    Logout endpoint - client side should remove tokens.
    
    This is just a dummy endpoint as token invalidation is handled client-side.
    In a more advanced implementation, you might want to add the token to a blocklist.
    """
    return {"detail": "Successfully logged out"}
