from app.core.schemas import Base


class TokenModel(Base):
    access_token: str
    refresh_token: str
    is_verified: bool


class TokenRefreshModel(Base):
    access_token: str