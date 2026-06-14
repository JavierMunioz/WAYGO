from typing import Any, Generic, TypeVar

from beanie import Document
from bson import ObjectId

from app.core.exceptions import NotFoundError

T = TypeVar("T", bound=Document)


class BaseRepository(Generic[T]):
    model: type[T]

    async def get_by_id(self, doc_id: str) -> T:
        try:
            obj_id = ObjectId(doc_id)
        except Exception:
            raise NotFoundError(f"{self.model.__name__} with id '{doc_id}' not found")
        doc = await self.model.get(obj_id)
        if not doc:
            raise NotFoundError(f"{self.model.__name__} with id '{doc_id}' not found")
        return doc

    async def get_by_id_or_none(self, doc_id: str) -> T | None:
        try:
            return await self.model.get(ObjectId(doc_id))
        except Exception:
            return None

    async def save(self, document: T) -> T:
        await document.save()
        return document

    async def delete(self, document: T) -> None:
        await document.delete()

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        query = self.model.find(filters or {})
        return await query.count()
