"""Usage dashboard endpoint."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ...services.usage import compute_usage


router = APIRouter()


@router.get("/usage")
async def usage():
    return JSONResponse(compute_usage())
