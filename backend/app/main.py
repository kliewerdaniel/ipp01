from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time

from app.core.config import settings
from app.api.routes import api_router
from app.core.security import (
    get_current_user, 
    CSRFProtectionMiddleware, 
    check_request_rate_limit
)
from app.db.init_db import check_and_init_db

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Rate limiting middleware
class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit the number of requests per IP address.
    """
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for certain paths
        if request.url.path == "/health" or request.url.path.startswith("/docs"):
            return await call_next(request)
            
        # Apply different rate limits based on the path
        if request.url.path.startswith(f"{settings.API_V1_STR}/auth/"):
            # Auth routes have their own rate limiting in the handler functions
            return await call_next(request)
        else:
            # General API rate limit
            if not check_request_rate_limit(
                request, 
                settings.API_RATE_LIMIT_PER_MINUTE, 
                60, 
                "api_rate"
            ):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please try again later."}
                )
        
        return await call_next(request)

# Add security-enhancing headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to responses.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), interest-cohort=()"
        
        return response

# Set up middleware (order matters)
# 1. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 2. Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# 3. CSRF protection middleware
app.add_middleware(CSRFProtectionMiddleware)

# 4. Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# 5. Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Calculate request processing time
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} completed in {process_time:.4f}s")
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Initialize database
@app.on_event("startup")
async def init_app():
    check_and_init_db()

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
