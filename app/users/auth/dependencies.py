import jwt
from fastapi import HTTPException, status, Security
from fastapi.security.api_key import APIKeyHeader

from app.core.settings import settings
from app.user.dependencies import get_user_service
from app.user.models import User
from loggers import get_logger

logger = get_logger(__name__)

access_token_header = APIKeyHeader(name="Authorization", scheme_name="access-token")
refresh_token_header = APIKeyHeader(name="Authorization", scheme_name="refresh-token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="could not validate credentials",
)
token_expired_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token has been expired")


async def get_current_user(
        token: str = Security(access_token_header),
) -> User:
    try:
        payload = jwt.decode(
            token, settings.jwt_user_secret_key, algorithms=[settings.algorithm]
        )
        id = payload.get("sub")
        mode = payload.get("mode")

        if id is None or mode != "access_token":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise token_expired_exception

    except jwt.InvalidTokenError:
        raise credentials_exception

    user = await get_user_service().get_single(id=id)
    if not user or user.is_deleted or user.is_blocked:
        raise credentials_exception

    return user


async def get_access_by_refresh_token(
        refresh_token: str = Security(refresh_token_header),
) -> User:
    try:
        payload = jwt.decode(
            refresh_token,
            settings.jwt_user_secret_key,
            algorithms=[settings.algorithm],
        )
        id = payload.get("sub")
        mode = payload.get("mode")

        if id is None or mode != "refresh_token":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise token_expired_exception

    except jwt.InvalidTokenError:
        raise credentials_exception

    user = await get_user_service().get_single(id=id)
    if not user or user.is_deleted or user.is_blocked:
        raise credentials_exception

    return user