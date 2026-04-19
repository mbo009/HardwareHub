from __future__ import annotations

import importlib.util
import sys
import urllib.error
from typing import Any

from app.assistant.llm_common import (
    data_url_to_mime_and_bytes,
    data_url_to_ollama_b64,
    effective_system_prompt,
    http_post_json,
    log_error,
    log_exception,
    user_text_for_vision_turn,
)
from app.assistant.model_capabilities import (
    openai_model_supports_images,
    resolve_ollama_images_enabled,
)

OLLAMA_VISION_APPENDIX = (
    "\n\nYou receive the image(s) as input. Follow WHEN IMAGES ARE PRESENT above: "
    'lead "message" with visible details and a best-effort identification before asking for missing fields. '
    "If the chat history mentions an earlier unrelated or joke image, ignore it for this turn — only describe the new photo(s). "
    "For purchaseDate default to today's SERVER CONTEXT date when appropriate; do not ask for purchase date in that case."
)

OLLAMA_TEXT_ONLY_WITH_IMAGES_MSG = (
    "The current model ({model}) is text-only — it cannot see photos. "
    "To scan hardware from images, install a vision model (fits ~8GB VRAM: "
    "`ollama pull llava:7b` or `ollama pull moondream` or `ollama pull qwen2.5vl:3b`), "
    "then set `OLLAMA_MODEL` to that tag in `.env` and restart the server. "
    "Or send a text message describing stickers, labels, or the device."
)

OPENAI_NO_VISION_MSG = (
    "The configured OpenAI model ({model}) is not treated as vision-capable here. "
    "Set OPENAI_MODEL to a vision model (e.g. gpt-4o-mini, gpt-4o) or describe the device in text."
)


def assistant_service_unavailable() -> dict[str, Any]:
    return {
        "message": "Service unavailable. Please try again later.",
        "proposal": None,
    }


def complete_assistant_json_raw(
    messages: list[dict[str, str]],
    images: list[str] | None,
    *,
    provider: str,
    api_key: str,
    model: str,
    ollama_base_url: str,
    ollama_image_mode: str,
    vision_user_index: int | None,
    system_prompt: str | None = None,
) -> str:
    """Single completion; returns raw model string (JSON)."""
    sys_p = system_prompt if system_prompt is not None else effective_system_prompt()
    prov = (provider or "mock").lower()

    if prov == "openai":
        from openai import OpenAI

        client = OpenAI(api_key=api_key, timeout=120.0, max_retries=2)
        openai_messages: list[dict[str, Any]] = [{"role": "system", "content": sys_p}]
        vidx = vision_user_index
        if vidx is None and images:
            if messages and messages[-1].get("role") == "user":
                vidx = len(messages) - 1
        for i, m in enumerate(messages):
            role = m.get("role")
            content = m.get("content") or ""
            if role not in ("user", "assistant"):
                continue
            if role == "user" and i == vidx and images:
                parts: list[dict[str, Any]] = [
                    {"type": "text", "text": user_text_for_vision_turn(content)},
                ]
                for img in images[:4]:
                    url = img.strip()
                    if not url.startswith("data:"):
                        url = f"data:image/jpeg;base64,{url}"
                    parts.append({"type": "image_url", "image_url": {"url": url}})
                openai_messages.append({"role": "user", "content": parts})
            else:
                openai_messages.append({"role": role, "content": content})

        resp = client.chat.completions.create(
            model=model,
            messages=openai_messages,
            response_format={"type": "json_object"},
            temperature=0.4,
        )
        return (resp.choices[0].message.content or "").strip() or "{}"

    if prov == "gemini":
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        try:
            contents: list[types.Content] = []
            vidx = vision_user_index
            if vidx is None and images:
                if messages and messages[-1].get("role") == "user":
                    vidx = len(messages) - 1
            for i, m in enumerate(messages):
                role, content = m.get("role"), m.get("content") or ""
                if role == "user":
                    if images is not None and vidx is not None and i == vidx:
                        t = user_text_for_vision_turn(content) if content.strip() else (
                            "Identify this hardware for company inventory."
                        )
                        last_parts: list[types.Part] = [types.Part.from_text(text=t)]
                        for img in images[:4]:
                            mime, raw = data_url_to_mime_and_bytes(img.strip())
                            last_parts.append(types.Part.from_bytes(data=raw, mime_type=mime))
                        contents.append(types.Content(role="user", parts=last_parts))
                    else:
                        contents.append(
                            types.Content(
                                role="user",
                                parts=[types.Part.from_text(text=(content or "").strip() or ".")],
                            )
                        )
                elif role == "assistant":
                    contents.append(
                        types.Content(role="model", parts=[types.Part.from_text(text=content)])
                    )

            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=sys_p,
                    temperature=0.4,
                    response_mime_type="application/json",
                ),
            )
            try:
                return ((response.text or "").strip() or "{}")
            except (ValueError, AttributeError):
                return "{}"
        finally:
            client.close()

    if prov == "ollama":
        base = (ollama_base_url or "").strip().rstrip("/")
        if not base:
            raise ValueError("empty Ollama base URL")
        model_name = (model or "").strip()
        if not model_name:
            raise ValueError("empty Ollama model name")

        vision = resolve_ollama_images_enabled(model_name, ollama_image_mode)
        if images and not vision:
            raise RuntimeError("ollama_text_only_with_images")

        vidx = vision_user_index
        if vidx is None and images:
            if messages and messages[-1].get("role") == "user":
                vidx = len(messages) - 1

        sys_ollama = sys_p + (OLLAMA_VISION_APPENDIX if (vision and images) else "")
        ollama_messages: list[dict[str, Any]] = [{"role": "system", "content": sys_ollama}]
        for i, m in enumerate(messages):
            role = m.get("role")
            content = m.get("content") or ""
            if role not in ("user", "assistant"):
                continue
            if role == "user" and i == vidx and images and vision:
                ollama_messages.append(
                    {
                        "role": "user",
                        "content": user_text_for_vision_turn(content),
                        "images": [data_url_to_ollama_b64(img) for img in images[:4]],
                    }
                )
            else:
                ollama_messages.append({"role": role, "content": content})

        payload: dict[str, Any] = {
            "model": model_name,
            "messages": ollama_messages,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.25 if (vision and images) else 0.4},
        }
        out = http_post_json(f"{base}/api/chat", payload, timeout_s=120.0)
        msg = out.get("message") or {}
        return (msg.get("content") or "").strip() or "{}"

    raise ValueError(f"unsupported provider for completion: {prov}")


def run_assistant(
    messages: list[dict[str, str]],
    images: list[str] | None,
    *,
    provider: str,
    api_key: str,
    model: str,
    ollama_base_url: str = "http://127.0.0.1:11434",
    ollama_image_mode: str = "auto",
) -> dict[str, Any]:
    prov = (provider or "mock").lower()

    if prov == "mock":
        return assistant_service_unavailable()

    if prov == "ollama":
        vision = resolve_ollama_images_enabled((model or "").strip(), ollama_image_mode)
        if images and not vision:
            return {
                "message": OLLAMA_TEXT_ONLY_WITH_IMAGES_MSG.format(model=model),
                "proposal": None,
            }
        try:
            from app.assistant.tool_loop import run_assistant_with_tools

            return run_assistant_with_tools(
                messages,
                images,
                provider=prov,
                api_key=api_key,
                model=model,
                ollama_base_url=ollama_base_url,
                ollama_image_mode=ollama_image_mode,
            )
        except urllib.error.URLError as e:
            log_error("Ollama request failed (network): " + str(e)[:500])
            return assistant_service_unavailable()
        except Exception:
            log_exception("Ollama assistant request failed")
            return assistant_service_unavailable()

    if prov not in ("openai", "gemini") or not api_key:
        return assistant_service_unavailable()

    if prov == "openai":
        if images and not openai_model_supports_images(model):
            return {"message": OPENAI_NO_VISION_MSG.format(model=model), "proposal": None}
        if importlib.util.find_spec("openai") is None:
            log_error(
                "assistant: OpenAI Python package is not installed "
                "(run: pip install -r backend/requirements.txt)"
            )
            return assistant_service_unavailable()
        try:
            from app.assistant.tool_loop import run_assistant_with_tools

            return run_assistant_with_tools(
                messages,
                images,
                provider=prov,
                api_key=api_key,
                model=model,
                ollama_base_url=ollama_base_url,
                ollama_image_mode=ollama_image_mode,
            )
        except Exception:
            log_exception("OpenAI assistant request failed")
            return assistant_service_unavailable()

    if prov == "gemini":
        if importlib.util.find_spec("google.genai") is None:
            log_error(
                "assistant: google-genai is not installed for this interpreter: "
                f"{sys.executable} (use project venv: backend\\.venv\\Scripts\\python.exe "
                "backend\\run.py, or: backend\\.venv\\Scripts\\pip install -r backend\\requirements.txt)"
            )
            return assistant_service_unavailable()
        from google.genai import errors as genai_errors

        try:
            from app.assistant.tool_loop import run_assistant_with_tools

            return run_assistant_with_tools(
                messages,
                images,
                provider=prov,
                api_key=api_key,
                model=model,
                ollama_base_url=ollama_base_url,
                ollama_image_mode=ollama_image_mode,
            )
        except genai_errors.APIError as e:
            code = getattr(e, "code", None)
            brief = (str(e) or "")[:900]
            if code == 429:
                log_error("Gemini quota / rate limit (429): " + brief)
            elif code == 404:
                log_error("Gemini model not found (404): " + brief)
            else:
                log_exception("Gemini API error")
            return assistant_service_unavailable()
        except Exception:
            log_exception("Gemini assistant request failed")
            return assistant_service_unavailable()

    return assistant_service_unavailable()
