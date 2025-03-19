from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserProfileUpdate
from app.core.security import get_password_hash, verify_password

logger = logging.getLogger(__name__)


def get_user_by_id(db: Session, id: str) -> Optional[User]:
    """
    Get a user by ID.
    """
    return db.query(User).filter(User.id == id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by email.
    """
    return db.query(User).filter(User.email == email).first()


def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_superuser: Optional[bool] = None
) -> List[User]:
    """
    Get all users with optional filtering.
    """
    query = db.query(User)
    
    if search:
        search = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search)) | (User.name.ilike(search))
        )
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if is_superuser is not None:
        query = query.filter(User.is_superuser == is_superuser)
    
    return query.offset(skip).limit(limit).all()


def create_user(db: Session, obj_in: UserCreate) -> User:
    """
    Create a new user.
    """
    # Check if email is already registered
    if get_user_by_email(db, email=obj_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user with hashed password
    db_obj = User(
        email=obj_in.email,
        name=obj_in.name,
        hashed_password=get_password_hash(obj_in.password),
        is_active=True,
        is_superuser=False,
    )
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    logger.info(f"Created new user: {db_obj.email}")
    return db_obj


def update_user(
    db: Session, 
    db_obj: User, 
    obj_in: Union[UserUpdate, Dict[str, Any]]
) -> User:
    """
    Update a user's data.
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    # Hash password if it's being updated
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Update user object with new data
    for field in update_data:
        if field != "password" and hasattr(db_obj, field):
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    logger.info(f"Updated user: {db_obj.email}")
    return db_obj


def update_user_profile(
    db: Session, 
    db_obj: User, 
    obj_in: UserProfileUpdate
) -> User:
    """
    Update a user's profile data.
    """
    update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        if hasattr(db_obj, field):
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    logger.info(f"Updated profile for user: {db_obj.email}")
    return db_obj


def delete_user(db: Session, db_obj: User) -> User:
    """
    Delete a user.
    """
    email = db_obj.email
    db.delete(db_obj)
    db.commit()
    
    logger.info(f"Deleted user: {email}")
    return db_obj


def change_password(
    db: Session, 
    db_obj: User, 
    current_password: str, 
    new_password: str
) -> User:
    """
    Change a user's password.
    """
    # Verify current password
    if not verify_password(current_password, db_obj.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    db_obj.hashed_password = get_password_hash(new_password)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    logger.info(f"Changed password for user: {db_obj.email}")
    return db_obj


def count_users(
    db: Session, 
    is_active: Optional[bool] = None,
    is_superuser: Optional[bool] = None
) -> int:
    """
    Count users with optional filtering.
    """
    query = db.query(User)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if is_superuser is not None:
        query = query.filter(User.is_superuser == is_superuser)
    
    return query.count()
