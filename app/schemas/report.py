from datetime import datetime

from pydantic import Field

from app.schemas.common import BaseSchema


class CreateReportRequest(BaseSchema):
    reason: str | None = Field(None, max_length=300)


class ReportResponse(BaseSchema):
    id: str
    target_type: str
    target_id: str
    status: str
    created_at: datetime
