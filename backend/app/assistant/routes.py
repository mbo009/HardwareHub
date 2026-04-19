import os
import re

from dotenv import load_dotenv
from flask import Blueprint, current_app, jsonify, request

from app.auth.decorators import login_required
from app.assistant.llm_client import run_assistant
from app.assistant.model_capabilities import assistant_llm_images_supported
from app.config import Config, refresh_llm_config_from_env

assistant_bp = Blueprint("assistant", __name__, url_prefix="/api/assistant")

MAX_IMAGES = 4
MAX_MESSAGE_LEN = 8000
MAX_HISTORY = 24

_STOCK_LOOKUP_HINT_RE = re.compile(
    r"(?i)"
    r"\b("
    r"do we have|"
    r"are there (any )?|"
    r"is there any|"
    r"how many|"
    r"what(?:'s| is) (?:in stock|available)|"
    r"czy mamy|"
    r"ile (?:jest|mamy)|"
    r"stan magazynu"
    r")\b|"
    r"\bany\b.+\bavailable\b"
)


def _message_looks_like_stock_lookup(text: str) -> bool:
    t = (text or "").strip()
    if len(t) < 4:
        return False
    return bool(_STOCK_LOOKUP_HINT_RE.search(t))


def _extract_inventory_search_query(text: str) -> str | None:
    """Map user wording to inventory_search query substring (ILIKE %query%)."""
    t = (text or "").lower()
    for word, q in (
        ("macbook", "mac"),
        ("thinkpad", "thinkpad"),
        ("chromebook", "chromebook"),
        ("surface", "surface"),
        ("iphone", "iphone"),
        ("ipad", "ipad"),
        ("dell", "dell"),
        ("lenovo", "lenovo"),
        ("samsung", "samsung"),
        ("monitor", "monitor"),
        ("sony", "sony"),
        ("logitech", "logitech"),
        ("razer", "razer"),
        ("microsoft", "microsoft"),
        ("asus", "asus"),
        ("acer", "acer"),
        ("hp", "hp"),
    ):
        if re.search(rf"\b{re.escape(word)}s?\b", t):
            return q
    if re.search(r"\bmacs?\b", t):
        return "mac"
    if re.search(r"\bmice\b", t) or re.search(r"\bmouses?\b", t) or re.search(r"\bmouse\b", t):
        return "mouse"
    if re.search(r"\bkeyboards?\b", t):
        return "keyboard"
    return None


def _infer_status_filter_for_stock_question(text: str) -> str | None:
    """
    None = all rows matching the name/brand query (any status: Rented, Available, …).
    Rentable = on-site and free to assign (excludes pre-arrival).
    Use Rentable only when the user clearly asks about renting/borrowing.
    Do NOT treat generic 'available' as SQL filter for 'how many X do we have' — that counts inventory.
    """
    t = (text or "").lower()
    if re.search(r"\b(rent|rental|wynaj|borrow|to rent|for rent)\b", t):
        return "Rentable"
    return None


def _deterministic_stock_reply(user_text: str) -> dict | None:
    """
    When the user asks a stock-style question and we can infer a device/brand token,
    answer purely from SQL — no LLM (avoids hallucinated counts when the model skips tools).
    """
    if not _message_looks_like_stock_lookup(user_text):
        return None
    q = _extract_inventory_search_query(user_text)
    if not q:
        return None
    from app.assistant.inventory_tools import format_inventory_tool_results_for_chat, inventory_search

    st = _infer_status_filter_for_stock_question(user_text)
    res = inventory_search(query=q, status=st, limit=80)
    tool_row = {
        "tool": "inventory_search",
        "arguments": {"query": q, "status": st},
        "ok": True,
        "result": res,
    }
    msg = format_inventory_tool_results_for_chat([tool_row])
    if not msg:
        return None
    return {"message": msg, "proposal": None}


@assistant_bp.route("/settings", methods=["GET", "OPTIONS"])
@login_required
def assistant_settings():
    if request.method == "OPTIONS":
        return "", 200

    load_dotenv(os.path.join(Config.repo_root, ".env"), override=True)
    refresh_llm_config_from_env(current_app)

    provider = (current_app.config.get("LLM_PROVIDER") or "mock").lower()
    ollama_base = (
        (current_app.config.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").strip().rstrip("/")
    )
    ollama_image_mode = (current_app.config.get("OLLAMA_IMAGE_MODE") or "auto").strip().lower()

    if provider == "openai":
        model = (current_app.config.get("OPENAI_MODEL") or "gpt-4o-mini").strip()
    elif provider == "gemini":
        model = (current_app.config.get("GEMINI_MODEL") or "gemini-2.0-flash-001").strip()
    elif provider == "ollama":
        model = (current_app.config.get("OLLAMA_MODEL") or "qwen3:8b").strip()
    else:
        model = ""

    images_supported = assistant_llm_images_supported(
        provider=provider,
        model=model,
        ollama_image_mode=ollama_image_mode,
    )

    return (
        jsonify(
            {
                "provider": provider,
                "model": model,
                "ollamaBaseUrl": ollama_base if provider == "ollama" else None,
                "ollamaImageMode": ollama_image_mode if provider == "ollama" else None,
                "imagesSupported": images_supported,
            }
        ),
        200,
    )


@assistant_bp.route("/chat", methods=["POST", "OPTIONS"])
@login_required
def chat():
    if request.method == "OPTIONS":
        return "", 200

    load_dotenv(os.path.join(Config.repo_root, ".env"), override=True)
    refresh_llm_config_from_env(current_app)

    data = request.get_json(silent=True) or {}
    messages_raw = data.get("messages")
    if not isinstance(messages_raw, list) or len(messages_raw) == 0:
        return jsonify({"error": "invalid_messages"}), 400

    messages: list[dict[str, str]] = []
    for m in messages_raw[-MAX_HISTORY:]:
        if not isinstance(m, dict):
            continue
        role = m.get("role")
        content = m.get("content")
        if role not in ("user", "assistant"):
            continue
        if not isinstance(content, str):
            content = str(content) if content is not None else ""
        if len(content) > MAX_MESSAGE_LEN:
            content = content[:MAX_MESSAGE_LEN]
        messages.append({"role": role, "content": content})

    if not messages or messages[-1]["role"] != "user":
        return jsonify({"error": "last_message_must_be_user"}), 400

    original_last_user_text = messages[-1]["content"]

    images_raw = data.get("images")
    images: list[str] | None = None
    if isinstance(images_raw, list) and images_raw:
        images = []
        for img in images_raw[:MAX_IMAGES]:
            if not isinstance(img, str):
                continue
            s = img.strip()
            if len(s) > 6_000_000:
                continue
            images.append(s)
        if not images:
            images = None

    if images and len(messages) >= 3:
        _vision_hint = (
            "\n\n[Inventory: identify hardware only from the image(s) in this message. "
            "Earlier messages may describe unrelated or joke content — ignore that for "
            "this identification and proposal.]"
        )
        _last = messages[-1]["content"]
        if "[Inventory: identify hardware only" not in _last:
            messages[-1]["content"] = _last + _vision_hint

    if not images and _message_looks_like_stock_lookup(messages[-1]["content"]):
        _stock_hint = (
            "\n\n[Reply mode: existing stock lookup — call inventory_search or inventory_stats via tool_calls "
            "with arguments YOU infer (e.g. query \"mac\", status \"Rentable\" for MacBooks available). "
            "Never ask the user to supply query/status. Answer from tool results. Set proposal to null. "
            "Do not describe hardware as if from a photo unless images were attached in this request.]"
        )
        _last = messages[-1]["content"]
        if "[Reply mode: existing stock lookup" not in _last:
            messages[-1]["content"] = _last + _stock_hint

    provider = (current_app.config.get("LLM_PROVIDER") or "mock").lower()
    ollama_base = (
        (current_app.config.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").strip().rstrip("/")
    )
    if provider == "openai":
        api_key = (current_app.config.get("OPENAI_API_KEY") or "").strip()
        model = (current_app.config.get("OPENAI_MODEL") or "gpt-4o-mini").strip()
        ollama_image_mode = "auto"
    elif provider == "gemini":
        api_key = (current_app.config.get("GEMINI_API_KEY") or "").strip()
        model = (current_app.config.get("GEMINI_MODEL") or "gemini-2.0-flash-001").strip()
        ollama_image_mode = "auto"
    elif provider == "ollama":
        api_key = ""
        model = (current_app.config.get("OLLAMA_MODEL") or "qwen3:8b").strip()
        ollama_image_mode = (current_app.config.get("OLLAMA_IMAGE_MODE") or "auto").strip().lower()
    else:
        api_key = ""
        model = ""
        ollama_image_mode = "auto"

    current_app.logger.warning(
        "assistant /chat: LLM_PROVIDER=%s model=%s images=%s openai_key_set=%s gemini_key_set=%s ollama_base=%s",
        provider,
        model,
        bool(images),
        bool((current_app.config.get("OPENAI_API_KEY") or "").strip()),
        bool((current_app.config.get("GEMINI_API_KEY") or "").strip()),
        ollama_base if provider == "ollama" else "",
    )

    if not images:
        direct = _deterministic_stock_reply(original_last_user_text)
        if direct is not None:
            return jsonify(direct), 200

    result = run_assistant(
        messages,
        images,
        provider=provider,
        api_key=api_key,
        model=model,
        ollama_base_url=ollama_base,
        ollama_image_mode=ollama_image_mode,
    )
    return jsonify(result), 200
