def login_admin(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "admin@test.com", "password": "Admin123!"},
    )
    assert res.status_code == 200


def login_user(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "user@test.com", "password": "pass123"},
    )
    assert res.status_code == 200


def test_admin_create_hardware_requires_auth(client):
    res = client.post(
        "/api/admin/hardware",
        json={"name": "MacBook Pro 16", "brand": "Apple"},
    )
    assert res.status_code == 401


def test_admin_create_hardware_forbidden_for_non_admin(client):
    login_user(client)
    res = client.post(
        "/api/admin/hardware",
        json={"name": "MacBook Pro 16", "brand": "Apple"},
    )
    assert res.status_code == 403


def test_admin_create_hardware_validates_required_fields(client):
    login_admin(client)
    res = client.post("/api/admin/hardware", json={"name": "", "brand": ""})
    assert res.status_code == 400
    assert res.get_json()["error"] == "invalid_name"


def test_admin_create_hardware_validates_status(client):
    login_admin(client)
    res = client.post(
        "/api/admin/hardware",
        json={"name": "MacBook Pro 16", "brand": "Apple", "status": "Broken"},
    )
    assert res.status_code == 400
    assert res.get_json()["error"] == "invalid_status"


def test_admin_create_hardware_success(client, app):
    from app.db import db
    from app.models import Hardware

    login_admin(client)
    res = client.post(
        "/api/admin/hardware",
        json={
            "name": "MacBook Pro 16",
            "brand": "Apple",
            "purchaseDate": "2026-03-01",
            "status": "Available",
            "assignedTo": "user@test.com",
            "notes": "Fresh device",
            "history": "Purchased in Q1",
        },
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["name"] == "MacBook Pro 16"
    assert data["brand"] == "Apple"
    assert data["purchaseDate"] == "2026-03-01"
    assert data["status"] == "Available"
    assert data["assignedTo"] == "user@test.com"

    with app.app_context():
        row = db.session.get(Hardware, data["id"])
        assert row is not None
        assert row.name == "MacBook Pro 16"
        assert row.brand == "Apple"
        assert row.status == "Available"


def test_admin_delete_hardware_requires_auth(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        row = Hardware(name="Delete Me", brand="Test", status="Available")
        db.session.add(row)
        db.session.commit()
        row_id = row.id

    res = client.delete(f"/api/admin/hardware/{row_id}")
    assert res.status_code == 401


def test_admin_delete_hardware_forbidden_for_non_admin(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        row = Hardware(name="Delete Me", brand="Test", status="Available")
        db.session.add(row)
        db.session.commit()
        row_id = row.id

    login_user(client)
    res = client.delete(f"/api/admin/hardware/{row_id}")
    assert res.status_code == 403


def test_admin_delete_hardware_not_found(client):
    login_admin(client)
    res = client.delete("/api/admin/hardware/999999")
    assert res.status_code == 404
    assert res.get_json()["error"] == "hardware_not_found"


def test_admin_delete_hardware_blocks_in_use_device(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        row = Hardware(
            name="In Use Device",
            brand="Test",
            status="In Use",
            assigned_to_email="user@test.com",
        )
        db.session.add(row)
        db.session.commit()
        row_id = row.id

    login_admin(client)
    res = client.delete(f"/api/admin/hardware/{row_id}")
    assert res.status_code == 409
    assert res.get_json()["error"] == "hardware_in_use"

    with app.app_context():
        still_exists = db.session.get(Hardware, row_id)
        assert still_exists is not None


def test_admin_delete_hardware_success(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        row = Hardware(name="Delete Me", brand="Test", status="Available")
        db.session.add(row)
        db.session.commit()
        row_id = row.id

    login_admin(client)
    res = client.delete(f"/api/admin/hardware/{row_id}")
    assert res.status_code == 200
    assert res.get_json()["ok"] is True

    with app.app_context():
        deleted = db.session.get(Hardware, row_id)
        assert deleted is None
