from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, func, Table, ForeignKey
from sqlalchemy.orm import relationship
from uuid import uuid4
import enum

from app.db.base_class import Base


class UserStatus(str, enum.Enum):
    """
    Enum for user status.
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class UserRole(str, enum.Enum):
    """
    Enum for user roles.
    """
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# Many-to-many relationship table for User-Permission
user_permissions = Table(
    "user_permissions",
    Base.metadata,
    Column("user_id", String, ForeignKey("user.id")),
    Column("permission_id", String, ForeignKey("permission.id")),
)


class Permission(Base):
    """
    Permission model for resource access control.
    """
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    resource = Column(String, nullable=False)  # Which resource this permission applies to
    action = Column(String, nullable=False)    # What action (read, write, delete, etc.)
    
    # Relationships
    users = relationship("User", secondary=user_permissions, back_populates="permissions")


class User(Base):
    """
    User model for storing user information.
    """
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Can be null for OAuth users
    name = Column(String, nullable=True)
    
    # Profile information
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    profile_image_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    job_title = Column(String, nullable=True)
    company = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    years_of_experience = Column(Integer, nullable=True)
    skills = Column(String, nullable=True)  # Comma-separated skills or JSON string
    
    # Subscription status
    current_subscription_id = Column(String, nullable=True)  # Reference to current active subscription
    subscription_status = Column(String, nullable=True)
    
    # Auth status
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING_VERIFICATION, nullable=False)
    
    # OAuth info
    oauth_provider = Column(String, nullable=True)
    oauth_id = Column(String, nullable=True)
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime, nullable=True)
    
    # Security
    failed_login_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime, nullable=True)
    locked_until = Column(DateTime, nullable=True)
    
    # Settings and preferences
    email_notifications = Column(Boolean, default=True)
    interface_language = Column(String, default="en", nullable=False)
    timezone = Column(String, default="UTC", nullable=False)
    
    # Timestamps
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    interviews = relationship("Interview", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="user", cascade="all, delete-orphan")
    permissions = relationship("Permission", secondary=user_permissions, back_populates="users")
    
    def has_permission(self, resource: str, action: str) -> bool:
        """
        Check if the user has the specified permission.
        Super admins always have all permissions.
        """
        if self.is_superuser or self.role == UserRole.SUPER_ADMIN:
            return True
            
        for permission in self.permissions:
            if permission.resource == resource and permission.action == action:
                return True
                
        return False
