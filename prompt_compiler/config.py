"""Application configuration and project paths."""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_ROOT / "config.json"
USAGE_FILE = PROJECT_ROOT / "usage.json"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"

DEFAULT_MODEL = "gemini-3.5-flash"

DEFAULT_CONFIG = {
    "gemini_api_key": "",
    "gemini_model": DEFAULT_MODEL,
    "system_prompt_override": "",
}


def load_config():
    """Load persisted settings, falling back to safe defaults on bad input."""
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open("r", encoding="utf-8") as config_file:
                data = json.load(config_file)
        except (OSError, json.JSONDecodeError):
            return dict(DEFAULT_CONFIG)
        return {
            "gemini_api_key": data.get("gemini_api_key", ""),
            "gemini_model": data.get("gemini_model", DEFAULT_MODEL),
            "system_prompt_override": data.get("system_prompt_override", ""),
        }
    return dict(DEFAULT_CONFIG)


def save_config(config):
    """Persist settings in the existing JSON format."""
    with CONFIG_FILE.open("w", encoding="utf-8") as config_file:
        json.dump(config, config_file, indent=2, ensure_ascii=False)
