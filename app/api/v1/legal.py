from fastapi import APIRouter, Request, status

from app.dependencies.auth import CurrentUser, SuperUser
from app.repositories.legal_repository import LegalDocumentRepository, UserConsentRepository
from app.schemas.legal import (
    ConsentRecordResponse,
    ConsentRequest,
    ConsentStatusResponse,
    CreateDocumentRequest,
    LegalDocumentResponse,
)
from app.services.legal_service import LegalService

router = APIRouter(prefix="/legal", tags=["Legal"])


def _get_service() -> LegalService:
    return LegalService(
        doc_repo=LegalDocumentRepository(),
        consent_repo=UserConsentRepository(),
    )


# ─── Public: document retrieval ──────────────────────────────────────────────

@router.get("/documents", response_model=list[LegalDocumentResponse])
async def list_active_documents():
    """Returns all currently active legal documents (one per type)."""
    return await _get_service().get_active_documents()


@router.get("/documents/{doc_type}", response_model=LegalDocumentResponse)
async def get_document(doc_type: str):
    """Returns the active legal document for the given type."""
    return await _get_service().get_document(doc_type)


@router.get("/documents/{doc_type}/versions", response_model=list[LegalDocumentResponse])
async def get_document_versions(doc_type: str):
    """Returns all historical versions of a document type."""
    return await _get_service().get_all_versions(doc_type)


# ─── Authenticated: consent ───────────────────────────────────────────────────

@router.get("/consent/status", response_model=ConsentStatusResponse)
async def get_consent_status(current_user: CurrentUser):
    """Returns whether the authenticated user has accepted all current legal documents."""
    return await _get_service().check_consent_status(str(current_user.id))


@router.post("/consent", status_code=status.HTTP_204_NO_CONTENT)
async def record_consent(data: ConsentRequest, request: Request, current_user: CurrentUser):
    """Records the authenticated user's acceptance of one or more legal documents."""
    ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else None)
    await _get_service().record_consent(str(current_user.id), data, ip)


# ─── Admin: document management ───────────────────────────────────────────────

@router.post("/admin/documents", response_model=LegalDocumentResponse, status_code=status.HTTP_201_CREATED)
async def publish_document(data: CreateDocumentRequest, _: SuperUser):
    """Publishes a new version of a legal document, deactivating the previous one."""
    svc = _get_service()
    return await svc.publish_document(
        doc_type=data.doc_type,
        version=data.version,
        title=data.title,
        content=data.content,
    )


@router.get("/admin/documents/{doc_type}/consents", response_model=list[ConsentRecordResponse])
async def get_document_consents(doc_type: str, version: str, _: SuperUser):
    """Lists all consent records for a specific document version."""
    svc = _get_service()
    consents = await svc.get_document_consents(doc_type, version)
    return [
        ConsentRecordResponse(
            id=str(c.id),
            user_id=c.user_id,
            doc_type=c.doc_type,
            doc_version=c.doc_version,
            accepted_at=c.accepted_at,
            platform=c.platform,
            app_version=c.app_version,
        )
        for c in consents
    ]
