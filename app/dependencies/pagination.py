from typing import Annotated

from fastapi import Query

from app.core.config import settings


class PaginationParams:
    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Page number"),
        page_size: int = Query(default=settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    ):
        self.page = page
        self.page_size = page_size


Pagination = Annotated[PaginationParams, None]
