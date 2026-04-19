from __future__ import annotations

_OLLAMA_VISION_SUBSTRINGS = frozenset(
    (
        "llava",
        "bakllava",
        "moondream",
        "cogvlm",
        "minicpm-v",
        "llama3.2-vision",
        "qwen2-vl",
        "qwen2.5-vl",
        "qwen2.5vl",
        "qwen3-vl",
        "internvl",
        "smolvlm",
        "gemma3",
        "phi3-vision",
    )
)

_OPENAI_VISION_SUBSTRINGS = frozenset(
    (
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4-vision",
        "gpt-4",
        "gpt-5",
        "o1",
        "o3",
        "o4",
        "vision",
    )
)


def ollama_model_supports_images(model: str) -> bool:
    m = (model or "").lower()
    return any(tok in m for tok in _OLLAMA_VISION_SUBSTRINGS)


def resolve_ollama_images_enabled(model: str, image_mode: str) -> bool:
    mode = (image_mode or "auto").lower().strip()
    if mode == "vision":
        return True
    if mode == "text":
        return False
    return ollama_model_supports_images(model)


def openai_model_supports_images(model: str) -> bool:
    u = (model or "").lower()
    if "gpt-3.5" in u:
        return False
    return any(x in u for x in _OPENAI_VISION_SUBSTRINGS)


def assistant_llm_images_supported(
    *,
    provider: str,
    model: str,
    ollama_image_mode: str = "auto",
) -> bool:
    prov = (provider or "").lower().strip()
    m = (model or "").strip()
    if prov in ("", "mock"):
        return False
    if prov == "ollama":
        return resolve_ollama_images_enabled(m, ollama_image_mode)
    if prov == "openai":
        return openai_model_supports_images(m)
    if prov == "gemini":
        return bool(m)
    return False
