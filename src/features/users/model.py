from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base, created_attp, updated_attp

if TYPE_CHECKING:
    from src.features.auth.model import RefreshTokenORM
    from src.features.posts.model import PostORM


class UserORM(Base):
    __tablename__ = "users_table"

    username: Mapped[str] = mapped_column(String(), unique=True, nullable=False)
    hashed_password: Mapped[bytes]

    updated_at: Mapped[updated_attp]
    created_at: Mapped[created_attp]

    posts: Mapped[List["PostORM"]] = relationship(back_populates="author")

    refresh_tokens: Mapped[List["RefreshTokenORM"]] = relationship(
        back_populates="user"
    )

    repr_cols = "username"
