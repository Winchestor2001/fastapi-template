from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.user.auth.dependencies import get_access_by_refresh_token
from app.user.auth.schemas import TokenModel, TokenRefreshModel
from app.user.auth.security import create_access_token, create_refresh_token
from app.user.dependencies import get_user_service
from app.user.models import User
from app.user.schemas import AuthModel, OtpVerifyModel, SendOTPModel
from app.user.services import UserService

router = APIRouter(prefix='/auth')
