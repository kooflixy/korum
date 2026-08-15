from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base, created_attp, updated_attp

if TYPE_CHECKING:
    from src.features.users.model import UserORM


class PostORM(Base):
    __tablename__ = "posts_table"

    title: Mapped[str] = mapped_column(String(256))
    content: Mapped[str] = mapped_column(default="")

    is_deleted: Mapped[bool] = mapped_column(default=False)

    author_id: Mapped[int] = mapped_column(ForeignKey("users_table.id"))
    author: Mapped["UserORM"] = relationship(back_populates="posts")

    updated_at: Mapped[updated_attp]
    created_at: Mapped[created_attp]
