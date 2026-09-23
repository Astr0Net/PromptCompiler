"""Supported model catalog and prompt categories."""

from collections import OrderedDict

from .config import DEFAULT_MODEL


MODELS = [
    {"id": "gemini-3.5-flash", "name": "Gemini 3.5 Flash", "category": "Text-out models", "rpm": 5, "tpm": 250_000, "rpd": 20, "generate": True},
    {"id": "gemini-3.8-flash", "name": "Gemini 3.8 Flash", "category": "Text-out models", "rpm": 5, "tpm": 250_000, "rpd": 20, "generate": True},
    {"id": "gemini-3.7-flash", "name": "Gemini 3.7 Flash", "category": "Text-out models", "rpm": 5, "tpm": 250_000, "rpd": 20, "generate": True},
    {"id": "gemini-3.6-flash", "name": "Gemini 3.6 Flash", "category": "Text-out models", "rpm": 5, "tpm": 250_000, "rpd": 20, "generate": True},
    {"id": "gemini-3.5-flash-lite", "name": "Gemini 3.5 Flash Lite", "category": "Text-out models", "rpm": 15, "tpm": 250_000, "rpd": 500, "generate": True},
    {"id": "gemini-3.1-pro", "name": "Gemini 3.1 Pro", "category": "Text-out models", "rpm": None, "tpm": None, "rpd": None, "generate": True},
    {"id": "gemini-3.1-flash-lite", "name": "Gemini 3.1 Flash Lite", "category": "Text-out models", "rpm": 15, "tpm": 250_000, "rpd": 500, "generate": True},
    {"id": "gemini-3-flash", "name": "Gemini 3 Flash", "category": "Text-out models", "rpm": 5, "tpm": 250_000, "rpd": 20, "generate": True},
    {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "category": "Text-out models", "rpm": None, "tpm": None, "rpd": None, "generate": True},
    {"id": "gemini-2.5-flash-lite", "name": "Gemini 2.5 Flash Lite", "category": "Text-out models", "rpm": 10, "tpm": 250_000, "rpd": 20, "generate": True},
    {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "category": "Text-out models", "rpm": 5, "tpm": 250_000, "rpd": 20, "generate": True},
    {"id": "gemini-2.0-flash-lite", "name": "Gemini 2 Flash Lite", "category": "Text-out models", "rpm": None, "tpm": None, "rpd": None, "generate": True},
    {"id": "gemini-2.0-flash", "name": "Gemini 2 Flash", "category": "Text-out models", "rpm": None, "tpm": None, "rpd": None, "generate": True},
    {"id": "antigravity", "name": "Antigravity", "category": "Agents", "rpm": 60, "tpm": 100_000, "rpd": 100, "generate": False},
    {"id": "deep-research-pro", "name": "Deep Research Pro Preview", "category": "Agents", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "computer-use-preview", "name": "Computer Use Preview", "category": "Other models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-2.5-flash-preview-image", "name": "Nano Banana (Gemini 2.5 Flash Preview Image)", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-2.5-flash-tts", "name": "Gemini 2.5 Flash TTS", "category": "Multi-modal generative models", "rpm": 3, "tpm": 10_000, "rpd": 10, "generate": False},
    {"id": "gemini-2.5-pro-tts", "name": "Gemini 2.5 Pro TTS", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-3-pro-image", "name": "Nano Banana Pro (Gemini 3 Pro Image)", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-3.1-flash", "name": "Nano Banana 2 (Gemini 3.1 Flash Image)", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-3.1-flash-lite-image", "name": "Nano Banana 2 Lite (Gemini 3.1 Flash Lite Image)", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-3.1-flash-tts", "name": "Gemini 3.1 Flash TTS", "category": "Multi-modal generative models", "rpm": 3, "tpm": 10_000, "rpd": 10, "generate": False},
    {"id": "gemini-3.5-transcribe", "name": "Gemini 3.5 Transcribe", "category": "Live API", "rpm": 3, "tpm": 10_000, "rpd": 25, "generate": False},
    {"id": "gemini-embedding-001", "name": "Gemini Embedding 1", "category": "Other models", "rpm": 100, "tpm": 30_000, "rpd": 1_000, "generate": False},
    {"id": "gemini-embedding-2", "name": "Gemini Embedding 2", "category": "Other models", "rpm": 100, "tpm": 30_000, "rpd": 1_000, "generate": False},
    {"id": "gemini-omni-1.1-flash", "name": "Gemini Omni 1.1 Flash", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-omni-flash", "name": "Gemini Omni Flash", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-robotics-er-2-preview", "name": "Gemini Robotics ER 2 Preview", "category": "Other models", "rpm": 5, "tpm": 250_000, "rpd": 20, "generate": False},
    {"id": "gemma-4-26b", "name": "Gemma 4 26B", "category": "Other models", "rpm": 30, "tpm": 16_000, "rpd": 14_400, "generate": False},
    {"id": "gemma-4-31b", "name": "Gemma 4 31B", "category": "Other models", "rpm": 30, "tpm": 16_000, "rpd": 14_400, "generate": False},
    {"id": "lyria-3-clip", "name": "Lyria 3 Clip", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "lyria-3-pro", "name": "Lyria 3 Pro", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "veo-3-fast-generate", "name": "Veo 3 Fast Generate", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "veo-3-generate", "name": "Veo 3 Generate", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "veo-3-lite-generate", "name": "Veo 3 Lite Generate", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-2.5-flash-native-audio-dialog", "name": "Gemini 2.5 Flash Native Audio Dialog", "category": "Live API", "rpm": None, "tpm": 1_000_000, "rpd": None, "generate": False},
    {"id": "gemini-3-flash-live", "name": "Gemini 3 Flash Live", "category": "Live API", "rpm": None, "tpm": 65_000, "rpd": None, "generate": False},
    {"id": "gemini-3.5-live-translate", "name": "Gemini 3.5 Live Translate", "category": "Live API", "rpm": None, "tpm": 20_000, "rpd": None, "generate": False},
    {"id": "gemini-3.5-transcribe-live", "name": "Gemini 3.5 Transcribe Live", "category": "Live API", "rpm": None, "tpm": 20_000, "rpd": None, "generate": False},
    {"id": "gemini-3.8-live", "name": "Gemini 3.8 Live", "category": "Live API", "rpm": None, "tpm": 65_000, "rpd": None, "generate": False},
    {"id": "gemini-3.8-live-extended-thinking", "name": "Gemini 3.8 Live Extended Thinking", "category": "Live API", "rpm": None, "tpm": 65_000, "rpd": None, "generate": False},
]

KNOWN_CATEGORIES = {
    "coding", "debugging", "research", "writing", "image_generation",
    "translation", "data_analysis", "planning", "automation", "general",
}


def group_models():
    groups = OrderedDict()
    for model in MODELS:
        groups.setdefault(model["category"], []).append(model)
    return groups
