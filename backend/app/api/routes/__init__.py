from fastapi import APIRouter

from app.api.routes import auth, users, interviews, questions, audio, payments, admin, subscriptions, webhooks

# Create the main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["Interviews"])
api_router.include_router(questions.router, prefix="/questions", tags=["Questions"])
api_router.include_router(audio.router, prefix="/audio", tags=["Audio Processing"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
