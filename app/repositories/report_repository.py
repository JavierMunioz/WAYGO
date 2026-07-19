from app.models.report import Report
from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository[Report]):
    model = Report

    async def exists(self, reporter_id: str, target_type: str, target_id: str) -> bool:
        existing = await Report.find_one(
            Report.reporter_id == reporter_id,
            Report.target_type == target_type,
            Report.target_id == target_id,
        )
        return existing is not None
