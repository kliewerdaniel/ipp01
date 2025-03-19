from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.user import UserResponse, UserUpdate, UserProfileUpdate, ChangePasswordRequest
from app.services.user import (
    get_user_by_id,
    update_user,
    update_user_profile,
    delete_user,
    change_password
)

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user profile.
    """
    db_user = get_user_by_id(db, id=current_user["id"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile.
    """
    db_user = get_user_by_id(db, id=current_user["id"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = update_user(db, db_obj=db_user, obj_in=user_update)
    return updated_user


@router.put("/me/profile", response_model=UserResponse)
async def update_user_additional_profile(
    profile_update: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's extended profile information.
    """
    db_user = get_user_by_id(db, id=current_user["id"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = update_user_profile(db, db_obj=db_user, obj_in=profile_update)
    return updated_user


@router.post("/me/change-password", response_model=UserResponse)
async def update_password(
    password_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    """
    db_user = get_user_by_id(db, id=current_user["id"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        updated_user = change_password(
            db, 
            db_obj=db_user, 
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/me", response_model=UserResponse)
async def delete_current_user(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user account (deactivate).
    """
    db_user = get_user_by_id(db, id=current_user["id"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Instead of actually deleting, we'll just deactivate
    db_user.is_active = False
    updated_user = update_user(db, db_obj=db_user, obj_in={"is_active": False})
    
    return updated_user
