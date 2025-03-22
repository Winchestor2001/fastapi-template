from fastapi import APIRouter, Depends

from app.user.auth.routers import router as user_auth_router

v1 = APIRouter()

user_prefix = "/users"

# ===== User auth ===== #
v1.include_router(user_auth_router, prefix=user_prefix, tags=["User Auth"])

