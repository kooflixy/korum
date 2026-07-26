from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base, created_attp, updated_attp


class PostORM(Base):
    __tablename__ = "posts_table"

    title: Mapped[str] = mapped_column(String(256))
    content: Mapped[str] = mapped_column(default="")

    updated_at: Mapped[updated_attp]
    created_at: Mapped[created_attp]
