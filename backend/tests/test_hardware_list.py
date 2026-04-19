from datetime import date, timedelta


def login_user(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "user@test.com", "password": "pass123"},
    )
    assert res.status_code == 200


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
                name="Dell XPS 15",
                brand="Dell",
                purchase_date=date(2026, 1, 20),
                status="In Use",
            ),
            Hardware(
                name="iPad Air",
                brand="Apple",
                purchase_date=date(2026, 2, 5),
                status="Repair",
            ),
        ]
        db.session.add_all(rows)
        db.session.commit()


def test_hardware_list_requires_auth(client):
    res = client.get("/api/hardware")
    assert res.status_code == 401


def test_hardware_list_returns_rows_for_logged_user(client, app):
    seed_hardware(app)
    login_user(client)
    res = client.get("/api/hardware")
    assert res.status_code == 200
    data = res.get_json()
    assert data["page"] == 1
    assert data["limit"] == 20
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["items"][0]["name"] == "Dell XPS 15"
    assert data["items"][1]["name"] == "MacBook Pro 16"
    assert data["items"][2]["name"] == "iPad Air"


def test_hardware_list_status_filter(client, app):
    seed_hardware(app)
    login_user(client)
    res = client.get("/api/hardware?status=Available")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "MacBook Pro 16"


def test_hardware_list_search_filter(client, app):
    seed_hardware(app)
    login_user(client)
    res = client.get("/api/hardware?search=apple")
    assert res.status_code == 200
    data = res.get_json()
    names = [item["name"] for item in data["items"]]
    assert names == ["MacBook Pro 16", "iPad Air"]


def test_hardware_list_brand_filter(client, app):
    seed_hardware(app)
    login_user(client)
    res = client.get("/api/hardware?brand=Apple")
    assert res.status_code == 200
    data = res.get_json()
    names = [item["name"] for item in data["items"]]
    assert names == ["MacBook Pro 16", "iPad Air"]


def test_hardware_list_date_range_filter(client, app):
    seed_hardware(app)
    login_user(client)
    res = client.get("/api/hardware?dateFrom=2026-01-16&dateTo=2026-02-01")
    assert res.status_code == 200
    data = res.get_json()
    names = [item["name"] for item in data["items"]]
    assert names == ["Dell XPS 15"]


def test_hardware_list_rejects_invalid_date_filter(client, app):
    seed_hardware(app)
    login_user(client)
    res = client.get("/api/hardware?dateFrom=not-a-date")
    assert res.status_code == 400
    assert res.get_json()["error"] == "invalid_date_from"


def test_hardware_list_pagination_returns_meta(client, app):
    seed_hardware(app)
    login_user(client)
    res = client.get("/api/hardware?page=1&limit=2")
    assert res.status_code == 200
    data = res.get_json()
    assert data["page"] == 1
    assert data["limit"] == 2
    assert data["total"] == 3
    assert data["totalPages"] == 2
    assert len(data["items"]) == 2


def test_hardware_list_rejects_invalid_pagination(client, app):
    seed_hardware(app)
    login_user(client)
    res = client.get("/api/hardware?page=0&limit=500")
    assert res.status_code == 400
    assert res.get_json()["error"] == "invalid_pagination"


def test_hardware_list_sort_desc_by_purchase_date(client, app):
    seed_hardware(app)
    login_user(client)
    res = client.get("/api/hardware?sortBy=purchaseDate&order=desc")
    assert res.status_code == 200
    data = res.get_json()
    names = [item["name"] for item in data["items"]]
    assert names == ["iPad Air", "Dell XPS 15", "MacBook Pro 16"]


def test_hardware_list_assigned_to_self_ok(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        row = Hardware(
            name="My Laptop",
            brand="Apple",
            purchase_date=date(2026, 1, 10),
            status="In Use",
            assigned_to_email="user@test.com",
        )
        db.session.add(row)
        db.session.commit()

    login_user(client)
    res = client.get("/api/hardware?assignedTo=user@test.com&status=In%20Use")
    assert res.status_code == 200
    data = res.get_json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "My Laptop"


def test_hardware_list_assigned_to_other_forbidden(client, app):
    seed_hardware(app)
    login_user(client)
    res = client.get("/api/hardware?assignedTo=admin@test.com")
    assert res.status_code == 403
    assert res.get_json()["error"] == "forbidden_assigned_to"


def test_hardware_list_includes_pre_arrival_for_future_purchase(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        db.session.add(
            Hardware(
                name="Future Thing",
                brand="Acme",
                purchase_date=date.today() + timedelta(days=14),
                status="Available",
            ),
        )
        db.session.commit()

    login_user(client)
    res = client.get("/api/hardware?search=Future")
    assert res.status_code == 200
    data = res.get_json()
    item = next(i for i in data["items"] if i["name"] == "Future Thing")
    assert item["preArrival"] is True


def test_hardware_list_status_ordered_filter(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        db.session.add(
            Hardware(
                name="Future Av",
                brand="Acme",
                purchase_date=date.today() + timedelta(days=7),
                status="Available",
            ),
        )
        db.session.add(
            Hardware(
                name="Future InUse",
                brand="Acme",
                purchase_date=date.today() + timedelta(days=7),
                status="In Use",
            ),
        )
        db.session.add(
            Hardware(
                name="Past Av",
                brand="Acme",
                purchase_date=date(2020, 1, 1),
                status="Available",
            ),
        )
        db.session.commit()

    login_user(client)
    res = client.get("/api/hardware?status=Ordered")
    assert res.status_code == 200
    data = res.get_json()
    names = [i["name"] for i in data["items"]]
    assert "Future Av" in names
    assert "Future InUse" not in names
    assert "Past Av" not in names


def test_hardware_list_status_unknown_filter(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        db.session.add(
            Hardware(
                name="Mystery Unit",
                brand="Acme",
                purchase_date=None,
                status="Unknown",
            ),
        )
        db.session.commit()

    login_user(client)
    res = client.get("/api/hardware?status=Unknown")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Mystery Unit"
