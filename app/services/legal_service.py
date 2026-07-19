from uuid import uuid4

from app.models.legal import LegalDocument, UserConsent
from app.repositories.legal_repository import LegalDocumentRepository, UserConsentRepository
from app.schemas.legal import ConsentItemRequest, ConsentRequest, ConsentStatusResponse, LegalDocumentResponse


def _to_response(doc: LegalDocument) -> LegalDocumentResponse:
    return LegalDocumentResponse(
        id=str(doc.id),
        doc_type=doc.doc_type,
        version=doc.version,
        title=doc.title,
        content=doc.content,
        effective_date=doc.effective_date,
    )


class LegalService:
    def __init__(
        self,
        doc_repo: LegalDocumentRepository,
        consent_repo: UserConsentRepository,
    ):
        self._docs = doc_repo
        self._consents = consent_repo

    async def get_active_documents(self) -> list[LegalDocumentResponse]:
        docs = await self._docs.get_active_documents()
        return [_to_response(d) for d in docs]

    async def get_document(self, doc_type: str) -> LegalDocumentResponse:
        from app.core.exceptions import NotFoundError
        doc = await self._docs.get_active_by_type(doc_type)
        if not doc:
            raise NotFoundError(f"Document '{doc_type}' not found")
        return _to_response(doc)

    async def check_consent_status(self, user_id: str) -> ConsentStatusResponse:
        active_docs = await self._docs.get_active_documents()
        user_consents = await self._consents.get_user_consents(user_id)

        accepted = {(c.doc_type, c.doc_version) for c in user_consents}
        pending = [
            _to_response(doc)
            for doc in active_docs
            if (doc.doc_type, doc.version) not in accepted
        ]

        return ConsentStatusResponse(
            is_compliant=len(pending) == 0,
            pending_documents=pending,
        )

    async def record_consent(
        self,
        user_id: str,
        request: ConsentRequest,
        ip_address: str | None,
    ) -> None:
        from app.core.exceptions import ValidationError

        for item in request.consents:
            doc = await self._docs.get_by_id(item.document_id)
            if not doc or doc.doc_type != item.doc_type or doc.version != item.doc_version:
                raise ValidationError(f"Invalid document reference: {item.document_id}")

            existing = await self._consents.get_user_consent_for_doc(
                user_id, item.doc_type, item.doc_version
            )
            if existing:
                continue  # Already recorded, idempotent

            consent = UserConsent(
                user_id=user_id,
                document_id=item.document_id,
                doc_type=item.doc_type,
                doc_version=item.doc_version,
                consent_uid=str(uuid4()),
                ip_address=ip_address,
                platform=request.platform,
                app_version=request.app_version,
            )
            await self._consents.create(consent)

    async def publish_document(
        self, doc_type: str, version: str, title: str, content: str
    ) -> LegalDocumentResponse:
        await self._docs.deactivate_type(doc_type)
        doc = LegalDocument(
            doc_type=doc_type,
            version=version,
            title=title,
            content=content,
        )
        await self._docs.create(doc)
        return _to_response(doc)

    async def get_document_consents(self, doc_type: str, doc_version: str) -> list[UserConsent]:
        return await self._consents.get_all_consents_for_document(doc_type, doc_version)

    async def get_all_versions(self, doc_type: str) -> list[LegalDocumentResponse]:
        docs = await self._docs.get_all_versions(doc_type)
        return [_to_response(d) for d in docs]
