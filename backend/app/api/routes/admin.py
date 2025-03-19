from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.db.session import get_db
from app.core.security import get_current_user, has_role, has_permission
from app.models.user import User, UserRole, Permission
from app.schemas.admin import (
    CloneRequest,
    CloneResponse,
    AdminDashboardStats,
    AdminUserManagement,
    AdminUserCreate,
    AdminUserUpdate
)
from app.schemas.user import (
    UserResponse, 
    UserAdminResponse, 
    UserRoleUpdate,
    UserStatusUpdate
)
from app.schemas.auth import (
    PermissionCreate,
    PermissionResponse,
    UserPermissionUpdate
)
from app.services.admin import (
    get_admin_dashboard_stats,
    create_platform_clone,
    get_admin_users,
    admin_update_user,
    admin_create_user
)
from app.services.user import get_user_by_id, get_users

router = APIRouter()

# We'll use the has_role dependency from the security module instead of creating our own
# This is a decorator that checks if the user has the ADMIN or SUPER_ADMIN role
admin_required = has_role(UserRole.ADMIN)
super_admin_required = has_role(UserRole.SUPER_ADMIN)

# We'll also use this permission-based dependency for finer-grained control
users_read = has_permission("users", "read")
users_write = has_permission("users", "write")


@router.get("/dashboard", response_model=AdminDashboardStats)
async def get_dashboard_stats(
    user: User = Depends(admin_required),
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
    user: User = Depends(super_admin_required),
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
    role_filter: Optional[UserRole] = None,
    user: User = Depends(users_read),
    db: Session = Depends(get_db)
):
    """
    Get all users with pagination and optional search.
    """
    users, total_count = get_admin_users(
        db,
        skip=skip,
        limit=limit,
        search=search,
        role_filter=role_filter
    )
    
    return AdminUserManagement(
        users=[UserResponse.model_validate(user) for user in users],
        total_count=total_count
    )


@router.get("/users/{user_id}", response_model=UserAdminResponse)
async def get_user(
    user_id: str = Path(..., title="The ID of the user to get"),
    user: User = Depends(users_read),
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


@router.put("/users/{user_id}", response_model=UserAdminResponse)
async def update_user(
    user_id: str,
    user_update: AdminUserUpdate,
    current_user: User = Depends(users_write),
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


@router.post("/users", response_model=UserAdminResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: AdminUserCreate,
    current_user: User = Depends(users_write),
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
            password=user_create.password,
            first_name=user_create.first_name,
            last_name=user_create.last_name
        )
        
        # Create user with specified role and admin flag
        user = admin_create_user(
            db, 
            user_data, 
            is_superuser=user_create.is_superuser,
            role=user_create.role
        )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )


# =========== Role Management Endpoints ===========

@router.put("/users/{user_id}/role", response_model=UserAdminResponse)
async def update_user_role(
    user_id: str,
    role_update: UserRoleUpdate,
    current_user: User = Depends(super_admin_required),
    db: Session = Depends(get_db)
):
    """
    Update a user's role. Only super admins can change roles.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Prevent changing the role of the last super admin
    if user.role == UserRole.SUPER_ADMIN and role_update.role != UserRole.SUPER_ADMIN:
        # Count super admins
        from sqlalchemy import func
        super_admin_count = db.query(func.count(User.id)).filter(
            User.role == UserRole.SUPER_ADMIN
        ).scalar()
        
        if super_admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote the last super admin"
            )
    
    # Update user's role
    user.role = role_update.role
    db.commit()
    db.refresh(user)
    
    return user


@router.put("/users/{user_id}/status", response_model=UserAdminResponse)
async def update_user_status(
    user_id: str,
    status_update: UserStatusUpdate,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Update a user's status (active, inactive, suspended, etc).
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Prevent changing the status of a super admin unless you are also a super admin
    if user.role == UserRole.SUPER_ADMIN and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can modify a super admin's status"
        )
    
    # Update user's status
    user.status = status_update.status
    db.commit()
    db.refresh(user)
    
    return user


# =========== Permission Management Endpoints ===========

@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    resource: Optional[str] = None,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    List all permissions, optionally filtered by resource.
    """
    query = db.query(Permission)
    
    if resource:
        query = query.filter(Permission.resource == resource)
    
    permissions = query.all()
    return [PermissionResponse.model_validate(permission) for permission in permissions]


@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission_create: PermissionCreate,
    current_user: User = Depends(super_admin_required),
    db: Session = Depends(get_db)
):
    """
    Create a new permission. Only super admins can create permissions.
    """
    # Check if permission already exists
    existing = db.query(Permission).filter(
        Permission.resource == permission_create.resource,
        Permission.action == permission_create.action
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Permission for {permission_create.resource}:{permission_create.action} already exists"
        )
    
    # Create the permission
    new_permission = Permission(
        name=permission_create.name,
        description=permission_create.description,
        resource=permission_create.resource,
        action=permission_create.action
    )
    
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    
    return new_permission


@router.put("/users/{user_id}/permissions", response_model=UserAdminResponse)
async def update_user_permissions(
    user_id: str,
    permission_update: UserPermissionUpdate,
    current_user: User = Depends(super_admin_required),
    db: Session = Depends(get_db)
):
    """
    Update a user's permissions. Only super admins can modify permissions.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Get permissions
    permissions = db.query(Permission).filter(
        Permission.id.in_(permission_update.permissions)
    ).all()
    
    if len(permissions) != len(permission_update.permissions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some permission IDs are invalid"
        )
    
    # Update user's permissions
    user.permissions = permissions
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/users/{user_id}/permissions", response_model=List[PermissionResponse])
async def get_user_permissions(
    user_id: str,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Get a user's permissions.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Get direct permissions
    direct_permissions = [PermissionResponse.model_validate(p) for p in user.permissions]
    
    # Include role-based permissions in the future
    return direct_permissions
