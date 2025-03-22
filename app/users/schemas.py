from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from pydantic import field_validator
from starlette import status

from app.core.enums import Lang
from app.core.schemas import Base
from app.core.validations import PHONE_NUMBER_PATTERN, USERNAME_VALIDATOR


class UserProfileViewModel(Base):
    id: UUID
    name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    username: Optional[str]
    language: Optional[Lang]
    avatar: Optional[str]
    is_verified: Optional[bool]

    @field_validator("username")
    def validate_username(cls, value):
        if value and not USERNAME_VALIDATOR.match(value):
            raise ValueError(
                """The username must start with a letter and consist of 4-30 characters,
                including latin letters, digits, and the underscore symbol.""")
        return value


class AuthModel(Base):
    phone_number: str
    lang: Lang

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if not PHONE_NUMBER_PATTERN.match(value):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Phone number must be entered in the format: +998 XX XXX XX XX")
        return value


class OtpVerifyModel(Base):
    phone_number: str
    otp: str


class SendOTPModel(Base):
    message: str
