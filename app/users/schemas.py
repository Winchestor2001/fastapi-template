from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from pydantic import field_validator
from starlette import status

from app.core.enums import Lang
from app.core.schemas import Base
from app.core.validations import PHONE_NUMBER_PATTERN, USERNAME_VALIDATOR
