import os

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
