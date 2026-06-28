from app.models.legal import LegalDocument, UserConsent


class LegalDocumentRepository:
    async def get_active_documents(self) -> list[LegalDocument]:
        return await LegalDocument.find(LegalDocument.is_active == True).to_list()

    async def get_active_by_type(self, doc_type: str) -> LegalDocument | None:
        return await LegalDocument.find_one(
            LegalDocument.doc_type == doc_type,
            LegalDocument.is_active == True,
        )

    async def get_by_id(self, doc_id: str) -> LegalDocument | None:
        from beanie import PydanticObjectId
        return await LegalDocument.get(PydanticObjectId(doc_id))

    async def deactivate_type(self, doc_type: str) -> None:
        await LegalDocument.find(LegalDocument.doc_type == doc_type).update(
            {"$set": {"is_active": False}}
        )

    async def create(self, doc: LegalDocument) -> LegalDocument:
        await doc.insert()
        return doc

    async def get_all_versions(self, doc_type: str) -> list[LegalDocument]:
        return (
            await LegalDocument.find(LegalDocument.doc_type == doc_type)
            .sort("-created_at")
            .to_list()
        )


class UserConsentRepository:
    async def get_user_consents(self, user_id: str) -> list[UserConsent]:
        return await UserConsent.find(UserConsent.user_id == user_id).to_list()

    async def get_user_consent_for_doc(
        self, user_id: str, doc_type: str, doc_version: str
    ) -> UserConsent | None:
        return await UserConsent.find_one(
            UserConsent.user_id == user_id,
            UserConsent.doc_type == doc_type,
            UserConsent.doc_version == doc_version,
        )

    async def create(self, consent: UserConsent) -> UserConsent:
        await consent.insert()
        return consent

    async def get_all_consents_for_document(
        self, doc_type: str, doc_version: str
    ) -> list[UserConsent]:
        return await UserConsent.find(
            UserConsent.doc_type == doc_type,
            UserConsent.doc_version == doc_version,
        ).to_list()
