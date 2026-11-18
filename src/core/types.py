from typing import Annotated

from pydantic import Field, StringConstraints

from src.core.config import settings

PG_INT_MIN = -2_147_483_648
PG_INT_MAX = 2_147_483_647

PgInt = Annotated[int, Field(ge=PG_INT_MIN, le=PG_INT_MAX)]
PgPositiveInt = Annotated[int, Field(gt=0, le=PG_INT_MAX)]


class PaginationParams:
    def __init__(
        self,
        page: PgPositiveInt = 1,
        per_page: PgPositiveInt = settings.RECORDS_COUNT_ON_PAGE,
    ):
        self.page = max(1, page)
        self.per_page = max(1, min(40, per_page))

        if self.per_page * (self.page - 1) > PG_INT_MAX:
            self.page = PG_INT_MAX // self.per_page


Username = Annotated[
    str,
    StringConstraints(
        min_length=5, max_length=64, pattern=r"^[a-zA-Z0-9_]+$", strip_whitespace=True
    ),
]
Password = Annotated[str, StringConstraints(min_length=8, max_length=72)]
