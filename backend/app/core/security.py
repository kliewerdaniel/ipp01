from datetime import datetime, timedelta
from typing import Optional, Union, Any, Dict, List
import secrets
import time
from uuid import uuid4

from fastapi import Depends, HTTPException, status, Request, Response, Cookie
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, ValidationError
import redis
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import get_db

# =========== Password Hashing ===========

# Password hashing context - using bcrypt with appropriate rounds
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

# =========== Rate Limiting ===========

# Redis client for rate limiting and token blacklisting
# In production, this should use a connection pool
redis_client = None
try:
    if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
        redis_client = redis.from_url(settings.REDIS_URL)
except:
    # Fall back to in-memory rate limiting if Redis is not available
    class InMemoryRateLimiter:
        def __init__(self):
            self.requests = {}
            self.blacklist = set()
            
        def incr(self, key, amount=1):
            current_time = int(time.time())
            # Clean up old entries
            self.requests = {k: v for k, v in self.requests.items() 
                            if v['timestamp'] > current_time - 3600}
            
            if key not in self.requests:
                self.requests[key] = {'count': 0, 'timestamp': current_time}
            
            self.requests[key]['count'] += amount
            return self.requests[key]['count']
            
        def ttl(self, key):
            return 3600  # 1 hour
            
        def expire(self, key, seconds):
            # We handle expiry in incr by checking timestamps
            pass
            
        def set(self, key, value, ex=None):
            self.blacklist.add(key)
            
        def get(self, key):
            if key in self.blacklist:
                return "1"
            return None
            
        def exists(self, key):
            return key in self.blacklist
    
    redis_client = InMemoryRateLimiter()

# =========== CSRF Protection ===========

# CSRF token secret
CSRF_SECRET = secrets.token_urlsafe(32)

def generate_csrf_token(session_id: str) -> str:
    """Generate a CSRF token."""
    return secrets.token_urlsafe(32)

def verify_csrf_token(token: str, session_id: str) -> bool:
    """Verify a CSRF token."""
    # Compare the token from the form/JSON with the one stored in the session
    # In a real implementation, check against a token stored in Redis or a DB
    if not token:
        return False
    
    # The actual implementation would look up the expected token for this session
    # If using Redis, you'd do something like:
    # expected_token = redis_client.get(f"csrf:{session_id}")
    # return token == expected_token
    
    # For now, we'll just ensure the token is non-empty, but this should be improved
    # with proper token validation against storage
    return bool(token)

# =========== Token Models ===========

class Token(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data model with user information."""
    sub: str
    exp: datetime
    jti: str  # JWT ID for token tracking/revocation
    role: Optional[str] = None
    permissions: Optional[List[str]] = None

class TokenPayload(BaseModel):
    """Payload extracted from a JWT token."""
    sub: Union[str, Any]
    exp: Optional[int] = None
    jti: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[List[str]] = None

# =========== Password Utilities ===========

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)

# =========== JWT Utilities ===========

def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None,
    role: Optional[str] = None,
    permissions: Optional[List[str]] = None
) -> str:
    """
    Create a JWT access token with role and permissions.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Create a unique ID for this token for potential revocation
    jti = str(uuid4())
    
    to_encode = {
        "sub": str(subject), 
        "exp": expire,
        "jti": jti,
        "iat": datetime.utcnow(),  # Issued at
    }
    
    # Add role and permissions if they exist
    if role:
        to_encode["role"] = role
    
    if permissions:
        to_encode["permissions"] = permissions
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(
    subject: Union[str, Any],
    role: Optional[str] = None
) -> str:
    """
    Create a JWT refresh token with longer expiry.
    """
    expire = datetime.utcnow() + timedelta(days=30)  # 30-day refresh token
    jti = str(uuid4())
    
    to_encode = {
        "sub": str(subject), 
        "exp": expire,
        "jti": jti,
        "iat": datetime.utcnow(),
        "token_type": "refresh"
    }
    
    if role:
        to_encode["role"] = role
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def revoke_token(token: str) -> None:
    """
    Revoke a JWT token by adding it to a blacklist.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        jti = payload.get("jti")
        exp = payload.get("exp")
        
        if jti and exp:
            # Store in Redis blacklist with expiry matching token
            current_time = int(time.time())
            ttl = max(exp - current_time, 0)
            redis_client.set(f"revoked:{jti}", "1", ex=ttl)
    except (JWTError, ValidationError):
        # If we can't decode the token, we can't revoke it
        pass

def is_token_revoked(jti: str) -> bool:
    """
    Check if a token has been revoked.
    """
    return redis_client.exists(f"revoked:{jti}")

# =========== OAuth2 Scheme with Cookie Support ===========

class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    """
    OAuth2 password bearer that can extract tokens from cookies as well as headers.
    """
    async def __call__(self, request: Request) -> Optional[str]:
        # First try to get the token from the Authorization header
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        
        if scheme.lower() == "bearer":
            return param
        
        # If no header token, try to get from cookie
        access_token = request.cookies.get("access_token")
        if access_token:
            return access_token
        
        # If no token found, raise 401 or return None based on auto_error
        if self.auto_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None

# Create the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# =========== Rate Limiting Functions ===========

def check_request_rate_limit(request: Request, limit: int, window: int, key_prefix: str) -> bool:
    """
    Check if a request exceeds rate limits.
    
    Args:
        request: The incoming request
        limit: Maximum number of requests allowed in the window
        window: Time window in seconds
        key_prefix: Prefix for the Redis key
        
    Returns:
        bool: True if request is within limits, False otherwise
    """
    # Get client IP - in production, consider X-Forwarded-For with appropriate validation
    client_ip = request.client.host if request.client else "unknown"
    key = f"{key_prefix}:{client_ip}"
    
    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, window)
    
    return count <= limit

def check_login_rate_limit(request: Request) -> bool:
    """Check login rate limits - 5 attempts per minute per IP."""
    return check_request_rate_limit(request, 5, 60, "login_rate")

def track_failed_login(user_id: str) -> bool:
    """
    Track failed login attempts for a user.
    Returns whether the account should be locked.
    """
    key = f"failed_login:{user_id}"
    count = redis_client.incr(key)
    
    # Set or refresh the expiry to 1 hour
    redis_client.expire(key, 3600)
    
    # Lock account after 5 failed attempts
    return count >= 5

def reset_failed_login(user_id: str) -> None:
    """Reset failed login counter after successful login."""
    key = f"failed_login:{user_id}"
    redis_client.delete(key)

# =========== User Authentication Functions ===========

async def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    """
    Decode JWT token to get current user with role and permissions.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        
        if user_id is None:
            raise credentials_exception
        
        # Check if token has been revoked
        if jti and is_token_revoked(jti):
            raise credentials_exception
        
        token_data = TokenPayload(
            sub=user_id, 
            jti=jti,
            role=payload.get("role"),
            permissions=payload.get("permissions")
        )
    except (JWTError, ValidationError):
        raise credentials_exception
    
    # Here you would fetch the user from the database
    from app.services.user import get_user_by_id
    
    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    
    # Check if user account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is temporarily locked due to too many failed login attempts",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Optional dependency to get current user (allows anonymous access)
async def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Optional dependency to get the current user. Returns None for unauthenticated requests.
    """
    # Try to get token from authorization header
    authorization = request.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(authorization)
    
    if not (scheme and token and scheme.lower() == "bearer"):
        # Try to get token from cookie
        token = request.cookies.get("access_token")
        if not token:
            return None
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        
        if not user_id:
            return None
        
        # Check if token has been revoked
        if jti and is_token_revoked(jti):
            return None
        
        # Get user from database
        from app.services.user import get_user_by_id
        user = get_user_by_id(db, user_id)
        return user
    except (JWTError, ValidationError):
        return None

# =========== Role and Permission Decorators ===========

def has_role(required_role: str):
    """
    Dependency to check if user has the required role.
    Example: @router.get("/admin-only", dependencies=[Depends(has_role("admin"))])
    """
    async def _has_role(user = Depends(get_current_user)):
        if user.role != required_role and not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: requires role '{required_role}'"
            )
        return user
    return _has_role

def has_permission(resource: str, action: str):
    """
    Dependency to check if user has the required permission.
    Example: @router.get("/users", dependencies=[Depends(has_permission("users", "read"))])
    """
    async def _has_permission(user = Depends(get_current_user)):
        if not user.has_permission(resource, action) and not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: requires {action} on {resource}"
            )
        return user
    return _has_permission

# =========== Cookie Handling ===========

def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """
    Set secure HTTP-only cookies for authentication.
    """
    # Set access token cookie - shorter lived
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Only sent over HTTPS
        samesite="lax",  # Helps prevent CSRF attacks
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",  # Available on all paths
    )
    
    # Set refresh token cookie - longer lived
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30 * 24 * 60 * 60,  # 30 days
        path=f"{settings.API_V1_STR}/auth/refresh",  # Only sent to refresh endpoint
    )
    
    # Set CSRF token - visible to JavaScript
    csrf_token = generate_csrf_token(access_token)
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        secure=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

def clear_auth_cookies(response: Response) -> None:
    """
    Clear authentication cookies on logout.
    """
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path=f"{settings.API_V1_STR}/auth/refresh")
    response.delete_cookie(key="csrf_token", path="/")

# =========== CSRF Middleware ===========

class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check CSRF tokens for unsafe HTTP methods.
    """
    async def dispatch(self, request: Request, call_next):
        # Skip CSRF check for safe methods (GET, HEAD, OPTIONS, TRACE)
        if request.method in ("GET", "HEAD", "OPTIONS", "TRACE"):
            return await call_next(request)
        
        # Skip CSRF check for APIs that handle authentication directly
        path = request.url.path
        if path.startswith(f"{settings.API_V1_STR}/auth/"):
            return await call_next(request)
        
        # Check for CSRF token in headers or form data
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token:
            try:
                form_data = await request.form()
                csrf_token = form_data.get("csrf_token")
            except:
                try:
                    json_data = await request.json()
                    csrf_token = json_data.get("csrf_token")
                except:
                    csrf_token = None
        
        # Get session ID from cookies
        session_id = request.cookies.get("access_token", "")
        
        # Verify CSRF token
        if not verify_csrf_token(csrf_token, session_id):
            return Response(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF token missing or invalid"}
            )
        
        return await call_next(request)
