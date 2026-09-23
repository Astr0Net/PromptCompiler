"""Model catalog endpoint."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ...catalog import MODELS


router = APIRouter()


@router.get("/models")
async def models():
    return JSONResponse(MODELS)
