"""Server-side inventory lookups for the assistant."""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import and_, func, or_

from app.db import db
from app.hardware.serialization import hardware_public_dict
from app.models import Hardware


def _available_on_site_clause():
    return (
        Hardware.status == "Available",
        or_(
            Hardware.purchase_date.is_(None),
            Hardware.purchase_date <= date.today(),
        ),
    )


def _ordered_pre_arrival_clause():
    return (
        Hardware.purchase_date.isnot(None),
        Hardware.purchase_date > date.today(),
        Hardware.status.in_(["Available", "Unknown"]),
    )


def inventory_search(
    query: str = "",
    status: str | None = None,
    limit: int = 40,
) -> dict[str, Any]:
    """
    Search hardware by substring in name or brand. status: Available, In Use,
    Repair, Unknown, Ordered (pre-arrival), Rentable (on-site + available to
    rent), or null/empty for all rows (still capped by limit).
    """
    lim = max(1, min(int(limit or 40), 80))
    q = Hardware.query
    st = (status or "").strip()
    if st.lower() == "rentable":
        q = q.filter(*_available_on_site_clause())
    elif st == "Ordered":
        q = q.filter(and_(*_ordered_pre_arrival_clause()))
    elif st:
        if st == "Available":
            q = q.filter(
                Hardware.status == "Available",
                or_(
                    Hardware.purchase_date.is_(None),
                    Hardware.purchase_date <= date.today(),
                ),
            )
        else:
            q = q.filter(Hardware.status == st)
    qn = (query or "").strip()
    if qn:
        like = f"%{qn}%"
        q = q.filter(
            or_(
                Hardware.name.ilike(like),
                Hardware.brand.ilike(like),
            )
        )
    q = q.order_by(Hardware.brand.asc(), Hardware.name.asc()).limit(lim)
    rows = q.all()
    items = []
    for h in rows:
        d = hardware_public_dict(h)
        notes = d.get("notes") or ""
        if isinstance(notes, str) and len(notes) > 220:
            notes = notes[:217] + "..."
        items.append(
            {
                "id": d["id"],
                "name": d["name"],
                "brand": d["brand"],
                "status": d["status"],
                "preArrival": d["preArrival"],
                "notes": notes or None,
            }
        )
    return {
        "returned": len(items),
        "limit": lim,
        "items": items,
    }


def inventory_stats(group_by: str = "status") -> dict[str, Any]:
    """Aggregate counts by status or brand (exact, from the database)."""
    gb = (group_by or "status").strip().lower()
    if gb == "brand":
        rows = (
            db.session.query(Hardware.brand, func.count(Hardware.id))
            .group_by(Hardware.brand)
            .order_by(func.count(Hardware.id).desc())
            .all()
        )
        counts = {str(b or ""): int(n) for b, n in rows}
        return {"groupBy": "brand", "counts": counts}
    rows = (
        db.session.query(Hardware.status, func.count(Hardware.id))
        .group_by(Hardware.status)
        .order_by(Hardware.status.asc())
        .all()
    )
    counts = {str(s): int(n) for s, n in rows}
    return {"groupBy": "status", "counts": counts}


def execute_assistant_tool(name: str, arguments: Any) -> dict[str, Any]:
    try:
        if name == "inventory_search":
            a = arguments if isinstance(arguments, dict) else {}
            try:
                lim = int(a.get("limit") or 40)
            except (TypeError, ValueError):
                lim = 40
            return {
                "ok": True,
                "result": inventory_search(
                    query=str(a.get("query") or ""),
                    status=a.get("status"),
                    limit=lim,
                ),
            }
        if name == "inventory_stats":
            a = arguments if isinstance(arguments, dict) else {}
            return {
                "ok": True,
                "result": inventory_stats(
                    group_by=str(a.get("group_by") or "status")
                ),
            }
        return {"ok": False, "error": f"unknown_tool:{name}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def run_assistant_tools(
    tool_calls: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for c in tool_calls:
        if not isinstance(c, dict):
            continue
        n = (c.get("name") or "").strip()
        args = c.get("arguments")
        if not isinstance(args, dict):
            args = {}
        if not n:
            continue
        r = execute_assistant_tool(n, args)
        out.append({"tool": n, "arguments": args, **r})
    return out


def format_inventory_tool_results_for_chat(
    tool_results: list[dict[str, Any]],
) -> str | None:
    """
    Build user-visible reply from DB tool output only.
    Returns None if there is nothing safe to format.
    """
    if not tool_results:
        return None
    blocks: list[str] = []
    for tr in tool_results:
        tool = (tr.get("tool") or "").strip()
        if not tr.get("ok"):
            err = tr.get("error") or "unknown error"
            blocks.append(f"Inventory lookup failed: {err}")
            continue
        if tool == "inventory_search":
            blocks.append(_format_one_inventory_search(tr))
        elif tool == "inventory_stats":
            blocks.append(_format_one_inventory_stats(tr.get("result") or {}))
    text = "\n\n".join(b for b in blocks if b)
    return text or None


def _format_one_inventory_search(tr: dict[str, Any]) -> str:
    res = tr.get("result") or {}
    args = tr.get("arguments") or {}
    n = int(res.get("returned") or 0)
    items = res.get("items") or []
    q = (args.get("query") or "").strip()
    st = args.get("status")
    st_disp = (str(st).strip() if st is not None else "") or "any"
    q_disp = f'matching "{q}"' if q else "with no name/brand filter"
    st_label = st_disp if st_disp != "any" else "any status"
    header = (
        f"Exact database matches {q_disp} "
        f"(status filter: {st_label}): {n} device(s)."
    )
    if n == 0:
        return header + " Nothing is listed under this search."
    lines: list[str] = []
    for it in items[:40]:
        nm = it.get("name") or "?"
        br = it.get("brand") or "?"
        stat = it.get("status") or "?"
        pre = it.get("preArrival")
        extra = " — not on site yet (pre-arrival)" if pre else ""
        lines.append(f"• {nm} ({br}) — {stat}{extra}")
    body = "\n".join(lines)
    if n > 40:
        body += f"\n… and {n - 40} more (limit)."
    return f"{header}\n{body}"


def _format_one_inventory_stats(res: dict[str, Any]) -> str:
    gb = res.get("groupBy") or "?"
    counts = res.get("counts") or {}
    if not counts:
        return f"No aggregate data returned (group by {gb})."
    parts = [
        f"{k}: {v}"
        for k, v in sorted(
            counts.items(),
            key=lambda x: (-x[1], str(x[0])),
        )
    ]
    return f"Exact counts by {gb} in the database: " + ", ".join(parts) + "."
