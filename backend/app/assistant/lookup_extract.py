"""Stage-1 extractor: NL query -> intent + tool calls."""

from __future__ import annotations

from typing import Any

from app.assistant import llm_client
from app.assistant.llm_common import (
    parse_assistant_model_json,
)

EXTRACT_SYSTEM_PROMPT = """
You are a planner for a hardware inventory assistant.

Given ONE user message, output JSON only:
{
  "intent": "intake_add" | "inventory_lookup" | "inventory_recommendation" | "other",
  "tool_calls": [
    {"name": "inventory_search", "arguments": {"query": "string or empty",
      "status": "Rentable|Available|In Use|Repair|Unknown|Ordered|null",
      "limit": 40}},
    {"name": "inventory_stats",
      "arguments": {"group_by": "status|brand"}}
  ],
  "reason": "short string"
}

Rules:
- For inventory_lookup/recommendation with no photo context, prefer
  at least one inventory_search call.
- Infer arguments from natural language (do not ask user for query/status/limit).
- Use status="Rentable" only if user clearly asks what can be rented/borrowed now.
- Use status="Ordered" for questions like "ordered", "on order", "pre-order",
  "arrives later", "not yet on site".
- Otherwise prefer status=null to include all inventory statuses.
- Use short query substring (e.g. "mac", "sony", "ipad", "laptop",
  "phone", "monitor", "keyboard", "mouse").
- For intake_add or unrelated/other messages, tool_calls can be [].
- Keep limit in [10, 80], default 40.
"""


def _normalize_tool_calls(raw_calls: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_calls, list):
        return []
    out: list[dict[str, Any]] = []
    for c in raw_calls:
        if not isinstance(c, dict):
            continue
        name = (c.get("name") or "").strip()
        if name not in {"inventory_search", "inventory_stats"}:
            continue
        args = c.get("arguments")
        if not isinstance(args, dict):
            args = {}
        if name == "inventory_search":
            q = str(args.get("query") or "").strip().lower()
            st = args.get("status")
            if st is None:
                st_norm = None
            else:
                st_txt = str(st).strip()
                st_norm = (
                    st_txt
                    if st_txt
                    in {"Rentable", "Available", "In Use", "Repair", "Unknown", "Ordered"}
                    else None
                )
            try:
                lim = int(args.get("limit") or 40)
            except (TypeError, ValueError):
                lim = 40
            lim = max(10, min(80, lim))
            out.append(
                {"name": "inventory_search", "arguments": {"query": q, "status": st_norm, "limit": lim}}
            )
        elif name == "inventory_stats":
            gb = str(args.get("group_by") or "status").strip().lower()
            if gb not in {"status", "brand"}:
                gb = "status"
            out.append({"name": "inventory_stats", "arguments": {"group_by": gb}})
    return out


def extract_lookup_plan(
    user_text: str,
    *,
    provider: str,
    api_key: str,
    model: str,
    ollama_base_url: str,
    ollama_image_mode: str,
) -> dict[str, Any] | None:
    msg = (user_text or "").strip()
    if not msg:
        return None
    raw = llm_client.complete_assistant_json_raw(
        [{"role": "user", "content": msg}],
        None,
        provider=provider,
        api_key=api_key,
        model=model,
        ollama_base_url=ollama_base_url,
        ollama_image_mode=ollama_image_mode,
        vision_user_index=None,
        system_prompt=EXTRACT_SYSTEM_PROMPT,
    )
    data = parse_assistant_model_json(raw)
    intent = (data.get("intent") or "").strip()
    if intent not in {"intake_add", "inventory_lookup", "inventory_recommendation", "other"}:
        intent = "other"
    return {
        "intent": intent,
        "tool_calls": _normalize_tool_calls(data.get("tool_calls")),
        "reason": str(data.get("reason") or "").strip(),
    }

