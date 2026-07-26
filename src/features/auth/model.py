from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base, created_attp, updated_attp


class UserORM(Base):
    __tablename__ = "users_table"

    username: Mapped[str] = mapped_column(String(), unique=True, nullable=False)
    hashed_password: Mapped[bytes]

    updated_at: Mapped[updated_attp]
    created_at: Mapped[created_attp]
