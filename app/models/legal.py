from datetime import UTC, datetime
from typing import Annotated, Literal

from beanie import Document, Indexed
from pydantic import Field


DocumentType = Literal["terms_and_conditions", "privacy_policy", "data_treatment_policy"]


class LegalDocument(Document):
    doc_type: Annotated[str, Indexed()]
    version: str
    title: str
    content: str
    is_active: bool = True
    effective_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "legal_documents"


class UserConsent(Document):
    user_id: Annotated[str, Indexed()]
    document_id: str
    doc_type: str
    doc_version: str
    consent_uid: str  # unique identifier for this specific consent record
    accepted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    ip_address: str | None = None
    platform: str | None = None  # "android" | "ios" | "web"
    app_version: str | None = None

    class Settings:
        name = "user_consents"
