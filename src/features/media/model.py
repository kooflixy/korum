from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.features.posts.model import PostORM

class MediaORM(Base):
    __tablename__ = 'media_table'

    file_key: Mapped[str] = mapped_column(unique=True, nullable=False)

    post_id: Mapped[Optional[int]] = mapped_column(ForeignKey("posts_table.id"))
    post: Mapped["PostORM"] = relationship(back_populates="media")

    comment_id: Mapped[Optional[int]]