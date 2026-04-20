from datetime import date

from app.assistant.inventory_tools import (
    format_inventory_tool_results_for_chat,
    inventory_search,
    inventory_stats,
)


def seed_hardware(app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        rows = [
            Hardware(
                name="MacBook Pro 16",
                brand="Apple",
                purchase_date=date(2026, 1, 15),
                status="Available",
            ),
            Hardware(
                name="MacBook Air 13",
                brand="Apple",
                purchase_date=date(2026, 1, 16),
                status="Available",
            ),
            Hardware(
                name="Dell XPS 15",
                brand="Dell",
                purchase_date=date(2026, 1, 20),
                status="In Use",
            ),
        ]
        db.session.add_all(rows)
        db.session.commit()


def test_inventory_search_mac_apple_available(app):
    seed_hardware(app)
    with app.app_context():
        r = inventory_search(query="mac", status="Available", limit=20)
    assert r["returned"] == 2
    assert all("Mac" in x["name"] for x in r["items"])


def test_inventory_stats_by_brand(app):
    seed_hardware(app)
    with app.app_context():
        r = inventory_stats(group_by="brand")
    assert r["groupBy"] == "brand"
    assert r["counts"].get("Apple") == 2
    assert r["counts"].get("Dell") == 1


def test_format_inventory_tool_results_lists_exact_count(app):
    seed_hardware(app)
    with app.app_context():
        r = inventory_search(query="dell", status=None, limit=20)
    tool_results = [
        {
            "tool": "inventory_search",
            "arguments": {"query": "dell", "status": None},
            "ok": True,
            "result": r,
        }
    ]
    msg = format_inventory_tool_results_for_chat(tool_results)
    assert msg is not None
    assert "1 device(s)" in msg or "1 device" in msg
    assert "Dell XPS 15" in msg


def test_inventory_search_rentable_excludes_future_pre_arrival(app):
    from app.db import db
    from app.models import Hardware

    seed_hardware(app)
    with app.app_context():
        db.session.add(
            Hardware(
                name="Future Mac",
                brand="Apple",
                purchase_date=date(2099, 1, 1),
                status="Available",
            )
        )
        db.session.commit()
        r = inventory_search(query="", status="Rentable", limit=20)
    names = {x["name"] for x in r["items"]}
    assert "Future Mac" not in names


def test_inventory_search_ordered_includes_future_available_unknown(app):
    from app.db import db
    from app.models import Hardware

    seed_hardware(app)
    with app.app_context():
        db.session.add_all(
            [
                Hardware(
                    name="Ordered Available Mac",
                    brand="Apple",
                    purchase_date=date(2099, 1, 1),
                    status="Available",
                ),
                Hardware(
                    name="Ordered Unknown Mac",
                    brand="Apple",
                    purchase_date=date(2099, 1, 2),
                    status="Unknown",
                ),
                Hardware(
                    name="Future In Use Mac",
                    brand="Apple",
                    purchase_date=date(2099, 1, 3),
                    status="In Use",
                ),
            ]
        )
        db.session.commit()
        r = inventory_search(query="", status="Ordered", limit=50)
    names = {x["name"] for x in r["items"]}
    assert "Ordered Available Mac" in names
    assert "Ordered Unknown Mac" in names
    assert "Future In Use Mac" not in names
