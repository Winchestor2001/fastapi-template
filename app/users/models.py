from datetime import datetime, date

from sqlalchemy import String, DateTime, ForeignKey, Boolean, Enum, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import Lang
from app.database.models import CommonMixin, Base


class User(CommonMixin, Base):
    __tablename__ = "users"  # noqa

    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    avatar_id: Mapped[int] = mapped_column(ForeignKey("avatar.id"), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    firebase_id: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    language: Mapped[Lang] = mapped_column(Enum(Lang, name="lang_enum", create_type=True), nullable=False)
    birthday: Mapped[date] = mapped_column(Date, nullable=True)
    last_deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    avatar = relationship("Avatar", back_populates="users")