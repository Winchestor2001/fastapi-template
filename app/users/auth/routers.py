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


@router.post('/', status_code=status.HTTP_200_OK, response_model=SendOTPModel)
async def register_user(
        user_form_data: AuthModel,
        user_service: Annotated[UserService, Depends(get_user_service)],
):
    """
    Registration users
    """
    return await user_service.send_otp(user_form_data)


@router.post('/refresh-token-new', status_code=status.HTTP_200_OK, response_model=TokenRefreshModel)
async def refresh_token(
        current_user: Annotated[User, Depends(get_access_by_refresh_token)],
):
    return TokenRefreshModel(
        access_token=create_access_token({"sub": str(current_user.id)})
    )
