from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.user.auth.dependencies import get_current_user
from app.user.dependencies import get_user_service
from app.user.models import User
from app.user.services import UserService
from loggers import get_logger

router = APIRouter(prefix='/profile')

logger = get_logger(__name__)
