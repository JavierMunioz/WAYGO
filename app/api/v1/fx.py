from fastapi import APIRouter

from app.schemas.fx import FxRatesResponse
from app.services.fx_service import FxService

router = APIRouter(prefix="/fx", tags=["FX"])


@router.get("/rates", response_model=FxRatesResponse)
async def get_rates():
    svc = FxService()
    rates, updated_at = await svc.get_rates()
    return FxRatesResponse(base="USD", rates=rates, updated_at=updated_at)
