import time
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import exc
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.database.database import async_session
from app.database.repositories import SQLAlchemyRepository
from app.user.domain.repositories import AbstractUserRepository
from app.user.exceptions import FilteringError
from app.user.models import User
from loggers import get_logger

logger = get_logger(__name__)


class UserRepository(SQLAlchemyRepository, AbstractUserRepository):
    """
    User repository
    """
    def __init__(self):
        super().__init__(User)
