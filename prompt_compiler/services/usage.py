"""Local token-usage persistence and aggregation."""

import json
import time
from datetime import datetime

from ..catalog import MODELS
from ..config import USAGE_FILE


def load_usage():
    if USAGE_FILE.exists():
        try:
            with USAGE_FILE.open("r", encoding="utf-8") as usage_file:
                data = json.load(usage_file)
            return data.get("events", [])
        except (OSError, json.JSONDecodeError):
            return []
    return []


def save_usage(events):
    with USAGE_FILE.open("w", encoding="utf-8") as usage_file:
        json.dump({"events": events}, usage_file, ensure_ascii=False)


def record_usage(model_id, usage):
    if not usage:
        return
    events = load_usage()
    now_ms = int(time.time() * 1000)
    events.append({
        "m": model_id,
        "t": now_ms,
        "in": usage.get("promptTokenCount", 0),
        "out": usage.get("candidatesTokenCount", 0),
        "th": usage.get("thoughtsTokenCount", 0),
        "tot": usage.get("totalTokenCount", 0),
    })
    cutoff = now_ms - 7 * 24 * 3600 * 1000
    save_usage([event for event in events if event["t"] >= cutoff])


def local_midnight_ms():
    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return int(midnight.timestamp() * 1000)


def compute_usage():
    events = load_usage()
    now_ms = int(time.time() * 1000)
    day_start = local_midnight_ms()
    minute_start = now_ms - 60000

    today_events = [event for event in events if event["t"] >= day_start]
    minute_events = [event for event in events if event["t"] >= minute_start]
    today_aggregate = {
        "requests": len(today_events),
        "input": sum(event["in"] for event in today_events),
        "output": sum(event["out"] for event in today_events),
        "thoughts": sum(event["th"] for event in today_events),
        "total": sum(event["tot"] for event in today_events),
    }

    model_usage = []
    for model in MODELS:
        model_today = [event for event in today_events if event["m"] == model["id"]]
        model_minute = [event for event in minute_events if event["m"] == model["id"]]
        model_usage.append({
            "id": model["id"],
            "name": model["name"],
            "category": model["category"],
            "rpm": model["rpm"],
            "tpm": model["tpm"],
            "rpd": model["rpd"],
            "today_requests": len(model_today),
            "today_tokens": sum(event["tot"] for event in model_today),
            "minute_requests": len(model_minute),
            "minute_tokens": sum(event["tot"] for event in model_minute),
        })
    return {"today": today_aggregate, "models": model_usage}
