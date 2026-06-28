from datetime import datetime

from app.schemas.common import BaseSchema


class LegalDocumentResponse(BaseSchema):
    id: str
    doc_type: str
    version: str
    title: str
    content: str
    effective_date: datetime


class ConsentItemRequest(BaseSchema):
    document_id: str
    doc_type: str
    doc_version: str


class ConsentRequest(BaseSchema):
    consents: list[ConsentItemRequest]
    platform: str | None = None
    app_version: str | None = None


class ConsentStatusResponse(BaseSchema):
    is_compliant: bool
    pending_documents: list[LegalDocumentResponse]


class CreateDocumentRequest(BaseSchema):
    doc_type: str
    version: str
    title: str
    content: str
    effective_date: datetime | None = None


class ConsentRecordResponse(BaseSchema):
    id: str
    user_id: str
    doc_type: str
    doc_version: str
    accepted_at: datetime
    platform: str | None
    app_version: str | None
