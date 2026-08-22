from typing import Annotated

from pydantic import StringConstraints

from src.core.config import settings


class PaginationParams:
    def __init__(self, page: int = 1, per_page: int = settings.RECORDS_COUNT_ON_PAGE):
        self.page = max(1, page)
        self.per_page = max(1, min(40, per_page))


Username = Annotated[
    str,
    StringConstraints(
        min_length=5, max_length=64, pattern=r"^[a-zA-Z0-9_]+$", strip_whitespace=True
    ),
]
Password = Annotated[str, StringConstraints(min_length=8, max_length=72)]
