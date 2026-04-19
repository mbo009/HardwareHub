from __future__ import annotations

import base64
import json
import logging
import os
import re
from datetime import date
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def log_error(message: str) -> None:
    _emit_log(message, exception=False)


def log_exception(message: str) -> None:
    _emit_log(message, exception=True)


def _emit_log(message: str, *, exception: bool) -> None:
    try:
        from flask import current_app, has_request_context

        if has_request_context():
            if exception:
                current_app.logger.exception(message)
            else:
                current_app.logger.error("%s", message)
            return
    except Exception:
        pass
    if exception:
        logger.exception(message)
    else:
        logger.error("%s", message)


def system_prompt_path() -> Path:
    override = (os.environ.get("ASSISTANT_SYSTEM_PROMPT_PATH") or "").strip()
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "prompts" / "system_prompt.txt"


def load_system_prompt() -> str:
    path = system_prompt_path()
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"assistant system prompt file is empty: {path}")
    return text


SYSTEM_PROMPT = load_system_prompt()


def effective_system_prompt() -> str:
    today_iso = date.today().isoformat()
    return (
        SYSTEM_PROMPT
        + "\n\n---\nSERVER CONTEXT (fixed for this session turn):\n"
        f"- Today is {today_iso} (YYYY-MM-DD, server local calendar date).\n"
        "- Apply the ACQUISITION DATE rules above using this date when defaulting purchaseDate.\n"
    )


def parse_json_response(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def parse_assistant_model_json(raw: str) -> dict[str, Any]:
    raw = raw.strip() or "{}"
    try:
        return parse_json_response(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end > start:
            return parse_json_response(raw[start : end + 1])
        raise


def normalize_proposal(data: dict[str, Any]) -> dict[str, Any] | None:
    prop = data.get("proposal")
    if not prop or not isinstance(prop, dict):
        return None
    if not prop.get("suggestAdd"):
        return None
    name = (prop.get("name") or "").strip()
    brand = (prop.get("brand") or "").strip()
    if not name or not brand:
        return None
    missing = prop.get("missingFields")
    if not isinstance(missing, list):
        missing = []
    serial = prop.get("serialNumber")
    if serial is not None and isinstance(serial, str):
        serial = serial.strip() or None
    notes = prop.get("notes")
    if notes is not None and isinstance(notes, str):
        notes = notes.strip() or None
    pd = prop.get("purchaseDate")
    if pd is not None and isinstance(pd, str):
        pd = pd.strip() or None
    status = (prop.get("status") or "Available").strip()
    if status not in {"Available", "In Use", "Repair", "Unknown"}:
        status = "Available"
    return {
        "suggestAdd": True,
        "name": name,
        "brand": brand,
        "serialNumber": serial,
        "purchaseDate": pd,
        "notes": notes,
        "status": status,
        "missingFields": [str(x) for x in missing],
    }


def assistant_reply_from_parsed(data: dict[str, Any]) -> dict[str, Any]:
    message = (data.get("message") or "").strip() or "Here is what I suggest."
    return {"message": message, "proposal": normalize_proposal(data)}


def assistant_reply_from_model_raw(raw: str) -> dict[str, Any]:
    return assistant_reply_from_parsed(parse_assistant_model_json(raw))


_GENERIC_USER_PHOTO_TEXT = frozenset(
    (
        "",
        "here are photos of the device.",
        "here are photos of the device",
    )
)

_VISION_USER_FALLBACK = (
    "Company hardware photos attached. Describe visible logos, labels, colors, and device type first, "
    "then your best-effort brand and model line before asking for serial or purchase date."
)


def user_text_for_vision_turn(content: str | None) -> str:
    c = (content or "").strip()
    if c.lower() in _GENERIC_USER_PHOTO_TEXT:
        return _VISION_USER_FALLBACK
    return c or _VISION_USER_FALLBACK


def data_url_to_mime_and_bytes(data_url: str) -> tuple[str, bytes]:
    s = (data_url or "").strip()
    if not s.startswith("data:"):
        return "image/jpeg", base64.b64decode(s, validate=False)
    comma = s.find(",")
    if comma == -1:
        raise ValueError("invalid image data")
    header, b64 = s[:comma], s[comma + 1 :]
    mime = "image/jpeg"
    if header.startswith("data:"):
        meta = header[5:]
        if ";base64" in meta:
            mime = meta.split(";base64", 1)[0].strip() or mime
        elif ";" in meta:
            mime = meta.split(";", 1)[0].strip() or mime
        else:
            mime = meta.strip() or mime
    return mime, base64.b64decode(b64, validate=False)


def data_url_to_ollama_b64(data_url: str) -> str:
    s = (data_url or "").strip()
    if s.startswith("data:") and "," in s:
        return s.split(",", 1)[1]
    return s


def http_post_json(url: str, payload: dict[str, Any], *, timeout_s: float = 120.0) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    import urllib.request

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return json.loads(raw)
