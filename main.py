"""Backward-compatible entry point for the refactored Prompt Compiler."""

from prompt_compiler.app import app
from prompt_compiler.catalog import DEFAULT_MODEL, KNOWN_CATEGORIES, MODELS, group_models
from prompt_compiler.config import CONFIG_FILE, USAGE_FILE, load_config, save_config
from prompt_compiler.prompt_engine import SYSTEM_PROMPT, parse_model_output
from prompt_compiler.services.gemini import call_gemini
from prompt_compiler.services.usage import (
    compute_usage,
    load_usage,
    local_midnight_ms,
    record_usage,
    save_usage,
)

__all__ = [
    "app",
    "DEFAULT_MODEL",
    "KNOWN_CATEGORIES",
    "MODELS",
    "group_models",
    "CONFIG_FILE",
    "USAGE_FILE",
    "load_config",
    "save_config",
    "SYSTEM_PROMPT",
    "parse_model_output",
    "call_gemini",
    "compute_usage",
    "load_usage",
    "local_midnight_ms",
    "record_usage",
    "save_usage",
]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
