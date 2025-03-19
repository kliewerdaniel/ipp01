from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.admin import (
    CloneRequest,
    CloneResponse,
    AdminDashboardStats,
    AdminUserManagement,
    AdminUserCreate,
    AdminUserUpdate
)
from app.schemas.user import UserResponse
from app.services.admin import (
    get_admin_dashboard_stats,
    create_platform_clone,
    get_admin_users,
    admin_update_user,
    admin_create_user
)
from app.services.user import get_user_by_id

router = APIRouter()


# Admin access check dependency
async def admin_check(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Check if the current user is an admin.
    Returns the current user if they are an admin, otherwise raises an exception.
    """
    user = get_user_by_id(db, current_user["id"])
    if not user or not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/dashboard", response_model=AdminDashboardStats)
async def get_dashboard_stats(
    _: dict = Depends(admin_check),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive statistics for the admin dashboard.
    """
    stats = get_admin_dashboard_stats(db)
    return stats


@router.post("/clone", response_model=CloneResponse, status_code=status.HTTP_201_CREATED)
async def create_clone(
    clone_request: CloneRequest,
    _: dict = Depends(admin_check),
    db: Session = Depends(get_db)
):
    """
    Create a new platform clone with custom branding.
    """
    try:
        clone = create_platform_clone(db, clone_request)
        return clone
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create clone: {str(e)}"
        )


@router.get("/users", response_model=AdminUserManagement)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    _: dict = Depends(admin_check),
    db: Session = Depends(get_db)
):
    """
    Get all users with pagination and optional search.
    """
    users, total_count = get_admin_users(
        db,
        skip=skip,
        limit=limit,
        search=search
    )
    
    return AdminUserManagement(
        users=[UserResponse.model_validate(user) for user in users],
        total_count=total_count
    )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    _: dict = Depends(admin_check),
    db: Session = Depends(get_db)
):
    """
    Get a user by ID.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: AdminUserUpdate,
    _: dict = Depends(admin_check),
    db: Session = Depends(get_db)
):
    """
    Update a user as admin.
    """
    try:
        updated_user = admin_update_user(db, user_id, user_update)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update user: {str(e)}"
        )


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: AdminUserCreate,
    _: dict = Depends(admin_check),
    db: Session = Depends(get_db)
):
    """
    Create a new user as admin.
    """
    try:
        from app.schemas.user import UserCreate
        
        # Convert AdminUserCreate to UserCreate
        user_data = UserCreate(
            email=user_create.email,
            name=user_create.name,
            password=user_create.password
        )
        
        # Create user with admin flag
        user = admin_create_user(db, user_data, is_superuser=user_create.is_superuser)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )
