import uuid
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import ForbiddenError, NotFoundError, StorageError
from app.models.photo import Photo
from app.repositories.photo_repository import PhotoRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.user_repository import UserRepository
from app.repositories.visit_repository import VisitRepository


class PhotoService:
    def __init__(
        self,
        photo_repo: PhotoRepository,
        visit_repo: VisitRepository,
        place_repo: PlaceRepository,
        user_repo: UserRepository,
    ):
        self._photo_repo = photo_repo
        self._visit_repo = visit_repo
        self._place_repo = place_repo
        self._user_repo = user_repo

    async def upload_photo(
        self,
        user_id: str,
        visit_id: str,
        place_id: str,
        file_content: bytes,
        content_type: str,
        caption: str | None = None,
    ) -> Photo:
        from app.core.constants import ALLOWED_IMAGE_TYPES, MAX_PHOTO_SIZE_MB

        if content_type not in ALLOWED_IMAGE_TYPES:
            raise StorageError(f"Unsupported image type: {content_type}")
        if len(file_content) > MAX_PHOTO_SIZE_MB * 1024 * 1024:
            raise StorageError(f"Image exceeds {MAX_PHOTO_SIZE_MB}MB limit")

        visit = await self._visit_repo.get_by_id(visit_id)
        if visit.user_id != user_id:
            raise ForbiddenError("Visit does not belong to this user")
        if not visit.verified:
            raise ForbiddenError("Only verified visits can have photos")

        image_url = await self._store_file(file_content, content_type)

        photo = Photo(
            user_id=user_id,
            place_id=place_id,
            visit_id=visit_id,
            image_url=image_url,
            caption=caption,
        )
        await photo.save()

        await self._place_repo.increment_counter(place_id, "total_photos")
        await self._user_repo.increment_counter(user_id, "photos_count")

        return photo

    async def get_photo(self, photo_id: str) -> Photo:
        return await self._photo_repo.get_by_id(photo_id)

    async def delete_photo(self, user_id: str, photo_id: str) -> None:
        photo = await self._photo_repo.get_by_id(photo_id)
        if photo.user_id != user_id:
            raise ForbiddenError("You can only delete your own photos")
        from beanie.operators import Set
        from datetime import UTC, datetime
        await Photo.find_one(Photo.id == photo.id).update(Set({"is_active": False}))
        await self._user_repo.increment_counter(user_id, "photos_count", amount=-1)

    async def get_user_photos(self, user_id: str, page: int, page_size: int) -> list[Photo]:
        from app.utils.pagination import compute_skip
        skip = compute_skip(page, page_size)
        return await self._photo_repo.get_user_photos(user_id, skip=skip, limit=page_size)

    async def get_place_photos(self, place_id: str, page: int, page_size: int) -> list[Photo]:
        from app.utils.pagination import compute_skip
        skip = compute_skip(page, page_size)
        return await self._photo_repo.get_place_photos(place_id, skip=skip, limit=page_size)

    async def _store_file(self, content: bytes, content_type: str) -> str:
        ext = content_type.split("/")[-1].replace("jpeg", "jpg")
        filename = f"{uuid.uuid4()}.{ext}"

        if settings.STORAGE_PROVIDER == "local":
            media_path = Path(settings.LOCAL_MEDIA_PATH)
            media_path.mkdir(parents=True, exist_ok=True)
            file_path = media_path / filename
            file_path.write_bytes(content)
            return f"{settings.STORAGE_CDN_URL}/{filename}"

        # S3 / Cloudflare R2 (boto3)
        try:
            import boto3
            client = boto3.client(
                "s3",
                region_name=settings.STORAGE_REGION,
                aws_access_key_id=settings.STORAGE_ACCESS_KEY,
                aws_secret_access_key=settings.STORAGE_SECRET_KEY,
            )
            client.put_object(
                Bucket=settings.STORAGE_BUCKET,
                Key=f"photos/{filename}",
                Body=content,
                ContentType=content_type,
            )
            return f"{settings.STORAGE_CDN_URL}/photos/{filename}"
        except Exception as e:
            raise StorageError(str(e))
