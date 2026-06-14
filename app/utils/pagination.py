from app.core.config import settings


def compute_skip(page: int, page_size: int) -> int:
    return (page - 1) * page_size


def clamp_page_size(page_size: int) -> int:
    return min(max(page_size, 1), settings.MAX_PAGE_SIZE)
