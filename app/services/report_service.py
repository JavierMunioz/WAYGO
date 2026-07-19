from app.core.exceptions import AlreadyExistsError
from app.models.report import Report
from app.repositories.photo_repository import PhotoRepository
from app.repositories.report_repository import ReportRepository


class ReportService:
    def __init__(self, report_repo: ReportRepository, photo_repo: PhotoRepository):
        self._repo = report_repo
        self._photo_repo = photo_repo

    async def report_photo(self, reporter_id: str, photo_id: str, reason: str | None) -> Report:
        await self._photo_repo.get_by_id(photo_id)  # 404 si no existe

        if await self._repo.exists(reporter_id, "photo", photo_id):
            raise AlreadyExistsError("Ya reportaste esta foto")

        report = Report(reporter_id=reporter_id, target_type="photo", target_id=photo_id, reason=reason)
        await report.save()
        return report
