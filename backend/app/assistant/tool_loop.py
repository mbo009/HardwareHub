"""Multi-step assistant: model may request inventory tools; server runs them and recalls the model."""

from __future__ import annotations

import json
from typing import Any

from app.assistant.inventory_tools import run_assistant_tools
from app.assistant.lookup_extract import extract_lookup_plan
from app.assistant.llm_common import (
    assistant_reply_from_parsed,
    assistant_reply_from_model_raw,
    effective_system_prompt,
    parse_assistant_model_json,
)
from app.assistant import llm_client

MAX_TOOL_ROUNDS = 5

TOOL_SYSTEM_APPENDIX = """
--- INVENTORY TOOLS (live database; no guessing counts) ---
Intents:
- intake_add: user is registering NEW company hardware (usually new photos or explicit intake details).
- inventory_lookup: user asks what exists in stock, counts, availability/rentability.
- inventory_recommendation: user asks which existing device should be rented for a use case
  (e.g. "mobile app testing", "cheap laptop for browsing only").

For inventory_lookup and inventory_recommendation with no new photos:
- You MUST call inventory_search and/or inventory_stats first.
- Set "proposal" to null.
- Do NOT ask for serial/model/purchase-date forms.
- Do NOT write "I see..." (there is no photo analysis in this path).

When the user asks about current stock, how many devices, what is available to rent, or which machine fits
a use case (e.g. cheap laptop for browsing), you MUST NOT invent numbers or device lists. Use the tools below
by filling "tool_calls" in your JSON. You may issue one or more tool calls in the same turn.

Available tools:
1) inventory_search — arguments: query (string, optional; matches name or brand, case-insensitive),
   status (optional: "Available", "Rentable", "In Use", "Repair", "Unknown", "Ordered", or null for any),
   limit (int, default 40, max 80).
   Use for "how many MacBooks", "Dell laptops available", "what can I rent", etc. Prefer status "Rentable"
   when the user means devices they can actually rent now (on site, not pre-arrival).
2) inventory_stats — arguments: group_by: "status" | "brand" — quick totals per status or brand.

YOU choose tool arguments — never ask the user for them:
- Employees speak in plain language only. Do NOT ask them to specify "query", "status", or "limit".
- Infer and fill arguments yourself, then call the tool in the same turn. Examples:
  • "how many MacBooks available" → inventory_search with query "mac" or "macbook", status "Rentable" (or
    "Available" if they clearly mean status label, not pre-arrival); count or summarize from returned rows.
  • "do we have iPads" → query "ipad", status "Rentable".
  • "what Dells are in stock" → query "dell", status null or "Rentable" depending on phrasing.
- "How many Sony / Logitech / Razer … do we have" (or similar) means rows in inventory for that brand —
  use query "sony" (etc.) and status null unless the user explicitly asks what is free to rent or on the shelf.
  Do not answer "none" just because nothing is status Available — Rented / In Use rows still count as inventory.
- If one query might miss rows (e.g. "MacBook" vs "Mac"), prefer a short substring like "mac" that matches both.
- Your reply after tools must be a normal sentence with numbers from tool results — not a form asking for filters.

After you receive tool results in a follow-up message:
- For inventory_lookup: report exact numbers/lists from tool output.
- For inventory_recommendation: pick candidates from returned rows and rank using your general product knowledge
  (typical device family positioning, portability, expected comfort for the use case). Be explicit that this is
  a best-effort estimate because the DB has no direct price/performance fields.
- If the user asks for "cheapest/basic" and available laptops look high-end, say that clearly and still propose
  the least overpowered option from current rentable devices.

Always include "tool_calls" in your JSON. Use an empty array [] when you do not need tools for this turn.
"""


def assistant_system_prompt_with_tools() -> str:
    return effective_system_prompt() + "\n\n" + TOOL_SYSTEM_APPENDIX


def _normalize_tool_calls(raw: dict[str, Any]) -> list[dict[str, Any]]:
    tc = raw.get("tool_calls")
    if not isinstance(tc, list):
        return []
    out: list[dict[str, Any]] = []
    for item in tc:
        if not isinstance(item, dict):
            continue
        name = (item.get("name") or "").strip()
        if not name:
            continue
        args = item.get("arguments")
        if args is not None and not isinstance(args, dict):
            args = {}
        out.append({"name": name, "arguments": args or {}})
    return out


def _tool_followup_user_content(tool_results: list[dict[str, Any]]) -> str:
    return (
        "Inventory tool results (authoritative; use only these facts for counts and listings):\n"
        + json.dumps(tool_results, ensure_ascii=False, indent=2)
        + "\n\nRespond with a single JSON object in the required format. Set tool_calls to []. "
        "Fill message for the user. proposal is usually null unless they are adding a new device."
    )


def _stage1_seed_for_lookup(
    messages: list[dict[str, str]],
    images: list[str] | None,
    *,
    provider: str,
    api_key: str,
    model: str,
    ollama_base_url: str,
    ollama_image_mode: str,
) -> list[dict[str, str]]:
    """
    Stage-1 (lightweight): use LLM to classify intent and infer initial tool calls.
    Stage-2 (main loop) then answers based on tool results.
    """
    if images or not messages:
        return []
    last = messages[-1]
    if last.get("role") != "user":
        return []
    user_text = (last.get("content") or "").strip()
    if not user_text:
        return []
    try:
        plan = extract_lookup_plan(
            user_text,
            provider=provider,
            api_key=api_key,
            model=model,
            ollama_base_url=ollama_base_url,
            ollama_image_mode=ollama_image_mode,
        )
    except Exception:
        return []
    if not isinstance(plan, dict):
        return []
    intent = (plan.get("intent") or "").strip()
    if intent not in {"inventory_lookup", "inventory_recommendation"}:
        return []
    tool_calls = plan.get("tool_calls")
    if not isinstance(tool_calls, list) or not tool_calls:
        return []
    results = run_assistant_tools(tool_calls)
    return [
        {
            "role": "assistant",
            "content": (
                "Planner stage: detected intent="
                + intent
                + ". Running initial inventory tools before final response."
            ),
        },
        {
            "role": "user",
            "content": _tool_followup_user_content(results),
        },
    ]


def run_assistant_with_tools(
    messages: list[dict[str, str]],
    images: list[str] | None,
    *,
    provider: str,
    api_key: str,
    model: str,
    ollama_base_url: str,
    ollama_image_mode: str,
) -> dict[str, Any]:
    prov = (provider or "mock").lower()
    suffix: list[dict[str, str]] = _stage1_seed_for_lookup(
        messages,
        images,
        provider=prov,
        api_key=api_key,
        model=model,
        ollama_base_url=ollama_base_url,
        ollama_image_mode=ollama_image_mode,
    )
    imgs = images
    last_raw = "{}"

    for _round in range(MAX_TOOL_ROUNDS):
        combined = messages + suffix
        raw_text = llm_client.complete_assistant_json_raw(
            combined,
            imgs,
            provider=prov,
            api_key=api_key,
            model=model,
            ollama_base_url=ollama_base_url,
            ollama_image_mode=ollama_image_mode,
            vision_user_index=(len(messages) - 1) if imgs else None,
            system_prompt=assistant_system_prompt_with_tools(),
        )
        last_raw = raw_text
        imgs = None

        try:
            data = parse_assistant_model_json(raw_text)
        except json.JSONDecodeError:
            return assistant_reply_from_model_raw(raw_text)

        tool_calls = _normalize_tool_calls(data)
        if not tool_calls:
            return assistant_reply_from_parsed(data)

        results = run_assistant_tools(tool_calls)
        brief = (data.get("message") or "").strip() or "Checking the inventory…"
        suffix.append({"role": "assistant", "content": brief})
        suffix.append({"role": "user", "content": _tool_followup_user_content(results)})

    try:
        data = parse_assistant_model_json(last_raw)
    except json.JSONDecodeError:
        return assistant_reply_from_model_raw(last_raw)
    data["tool_calls"] = []
    if not (data.get("message") or "").strip():
        data["message"] = (
            "I could not finish loading inventory. Try a shorter question or check the dashboard."
        )
    return assistant_reply_from_parsed(data)
