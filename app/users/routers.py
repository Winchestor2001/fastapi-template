from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.user.auth.dependencies import get_current_user
from app.user.dependencies import get_user_service
from app.user.models import User
from app.user.schemas import UserProfileViewModel
from app.user.services import UserService
from loggers import get_logger

router = APIRouter(prefix='/profile')

logger = get_logger(__name__)


@router.get('/me', status_code=status.HTTP_200_OK, response_model=UserProfileViewModel)
async def get_profile(
        current_user: Annotated[User, Depends(get_current_user)],
        user_service: Annotated[UserService, Depends(get_user_service)],
):
    user = await user_service.get_single(id=current_user.id)
    return user
