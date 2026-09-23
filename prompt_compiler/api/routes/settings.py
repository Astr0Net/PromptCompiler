"""Settings endpoint."""

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse

from ...catalog import DEFAULT_MODEL
from ...config import save_config


router = APIRouter()


@router.post("/settings")
async def update_settings(
    gemini_api_key: str = Form(""),
    gemini_model: str = Form(DEFAULT_MODEL),
    system_prompt_override: str = Form(""),
):
    save_config({
        "gemini_api_key": gemini_api_key.strip(),
        "gemini_model": gemini_model.strip() or DEFAULT_MODEL,
        "system_prompt_override": system_prompt_override,
    })
    return JSONResponse({"status": "ok", "message": "Settings saved"})
