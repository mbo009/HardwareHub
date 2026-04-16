from datetime import date


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
    assert len(data) == 3
    assert data[0]["name"] == "Dell XPS 15"
    assert data[1]["name"] == "MacBook Pro 16"
    assert data[2]["name"] == "iPad Air"


def test_hardware_list_status_filter(client, app):
    seed_hardware(app)
    login_user(client)
    res = client.get("/api/hardware?status=Available")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "MacBook Pro 16"


def test_hardware_list_search_filter(client, app):
    seed_hardware(app)
    login_user(client)
    res = client.get("/api/hardware?search=apple")
    assert res.status_code == 200
    data = res.get_json()
    names = [item["name"] for item in data]
    assert names == ["MacBook Pro 16", "iPad Air"]


def test_hardware_list_sort_desc_by_purchase_date(client, app):
    seed_hardware(app)
    login_user(client)
    res = client.get("/api/hardware?sortBy=purchaseDate&order=desc")
    assert res.status_code == 200
    data = res.get_json()
    names = [item["name"] for item in data]
    assert names == ["iPad Air", "Dell XPS 15", "MacBook Pro 16"]
