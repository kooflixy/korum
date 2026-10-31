from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base

if TYPE_CHECKING:
    from src.features.posts.model import PostORM


class MediaStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"


class MediaORM(Base):
    __tablename__ = "media_table"

    file_key: Mapped[str] = mapped_column(unique=True, nullable=False)
    status: Mapped[MediaStatus] = mapped_column(
        SAEnum(
            MediaStatus,
            name="media_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=MediaStatus.READY,
        nullable=False,
    )

    post_id: Mapped[int] = mapped_column(ForeignKey("posts_table.id"))
    post: Mapped["PostORM"] = relationship(back_populates="media")
