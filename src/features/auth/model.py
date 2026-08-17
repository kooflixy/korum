import datetime
from typing import TYPE_CHECKING, Annotated, Optional

from sqlalchemy import DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.config import settings
from src.db.database import Base, created_attp

if TYPE_CHECKING:
    from src.features.users.model import UserORM

expires_attp = Annotated[
    datetime.datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=text(
            f"TIMEZONE('utc', now()) + INTERVAL '{settings.REFRESH_TOKEN_EXPIRE_DAYS} days'"
        ),
    ),
]


class RefreshTokenORM(Base):
    __tablename__ = "refresh_tokens_table"

    user_id: Mapped[int] = mapped_column(ForeignKey("users_table.id"))
    user: Mapped["UserORM"] = relationship(back_populates="refresh_tokens")

    token_hash: Mapped[bytes] = mapped_column(unique=True)

    ip_address: Mapped[Optional[str]]
    device_info: Mapped[Optional[str]]

    is_revoked: Mapped[bool] = mapped_column(default=False)
    is_used: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[created_attp]
    expires_at: Mapped[expires_attp]

    repr_cols = ("user_id", "device_info", "is_revoked", "is_used", "expires_at")
