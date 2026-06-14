import uuid
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import StorageError


async def store_file(content: bytes, content_type: str) -> str:
    ext = content_type.split("/")[-1].replace("jpeg", "jpg")
    filename = f"{uuid.uuid4()}.{ext}"

    if settings.STORAGE_PROVIDER == "local":
        media_path = Path(settings.LOCAL_MEDIA_PATH)
        media_path.mkdir(parents=True, exist_ok=True)
        (media_path / filename).write_bytes(content)
        return f"{settings.STORAGE_CDN_URL}/{filename}"

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
            Key=f"media/{filename}",
            Body=content,
            ContentType=content_type,
        )
        return f"{settings.STORAGE_CDN_URL}/media/{filename}"
    except Exception as e:
        raise StorageError(str(e))
