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
            "serialNumber": "MBP-2026-001",
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
    assert data["serialNumber"] == "MBP-2026-001"
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


def test_admin_mark_hardware_repair_requires_auth(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        row = Hardware(name="Needs Repair", brand="Test", status="Available")
        db.session.add(row)
        db.session.commit()
        row_id = row.id

    res = client.patch(f"/api/admin/hardware/{row_id}/repair")
    assert res.status_code == 401


def test_admin_mark_hardware_repair_forbidden_for_non_admin(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        row = Hardware(name="Needs Repair", brand="Test", status="Available")
        db.session.add(row)
        db.session.commit()
        row_id = row.id

    login_user(client)
    res = client.patch(f"/api/admin/hardware/{row_id}/repair")
    assert res.status_code == 403


def test_admin_mark_hardware_repair_not_found(client):
    login_admin(client)
    res = client.patch("/api/admin/hardware/999999/repair")
    assert res.status_code == 404
    assert res.get_json()["error"] == "hardware_not_found"


def test_admin_mark_hardware_repair_unassigns_in_use_device(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        row = Hardware(
            name="Leased Device",
            brand="Test",
            status="In Use",
            assigned_to_email="user@test.com",
        )
        db.session.add(row)
        db.session.commit()
        row_id = row.id

    login_admin(client)
    res = client.patch(f"/api/admin/hardware/{row_id}/repair")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "Available"
    assert data["assignedTo"] is None
    assert data["wasInUse"] is True

    with app.app_context():
        updated = db.session.get(Hardware, row_id)
        assert updated is not None
        assert updated.status == "Available"
        assert updated.assigned_to_email is None


def test_admin_mark_hardware_repair_toggles_repair_to_available(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        row = Hardware(name="Repair Device", brand="Test", status="Repair")
        db.session.add(row)
        db.session.commit()
        row_id = row.id

    login_admin(client)
    res = client.patch(f"/api/admin/hardware/{row_id}/repair")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "Available"
    assert data["wasInUse"] is False

    with app.app_context():
        updated = db.session.get(Hardware, row_id)
        assert updated is not None
        assert updated.status == "Available"


def test_admin_update_hardware_requires_auth(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        row = Hardware(
            name="Old Device",
            brand="Old Brand",
            status="Available",
        )
        db.session.add(row)
        db.session.commit()
        row_id = row.id

    res = client.patch(
        f"/api/admin/hardware/{row_id}",
        json={"name": "New Device"},
    )
    assert res.status_code == 401


def test_admin_update_hardware_forbidden_for_non_admin(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        row = Hardware(
            name="Old Device",
            brand="Old Brand",
            status="Available",
        )
        db.session.add(row)
        db.session.commit()
        row_id = row.id

    login_user(client)
    res = client.patch(
        f"/api/admin/hardware/{row_id}",
        json={"name": "New Device"},
    )
    assert res.status_code == 403


def test_admin_update_hardware_updates_name_brand_and_serial(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        row = Hardware(
            name="Old Device",
            brand="Old Brand",
            status="Available",
        )
        db.session.add(row)
        db.session.commit()
        row_id = row.id

    login_admin(client)
    res = client.patch(
        f"/api/admin/hardware/{row_id}",
        json={
            "name": "MacBook Pro 14",
            "brand": "Apple",
            "serialNumber": "MBP-2026-001",
        },
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["name"] == "MacBook Pro 14"
    assert data["brand"] == "Apple"
    assert data["serialNumber"] == "MBP-2026-001"


def test_admin_update_hardware_sets_in_use_with_assigned_user(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        row = Hardware(name="Device", brand="Brand", status="Available")
        db.session.add(row)
        db.session.commit()
        row_id = row.id

    login_admin(client)
    res = client.patch(
        f"/api/admin/hardware/{row_id}",
        json={"status": "In Use", "assignedTo": "user@test.com"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "In Use"
    assert data["assignedTo"] == "user@test.com"


def test_admin_update_hardware_in_use_requires_assigned_user(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        row = Hardware(name="Device", brand="Brand", status="Available")
        db.session.add(row)
        db.session.commit()
        row_id = row.id

    login_admin(client)
    res = client.patch(
        f"/api/admin/hardware/{row_id}",
        json={"status": "In Use"},
    )
    assert res.status_code == 400
    assert res.get_json()["error"] == "assigned_to_required_for_in_use"


def test_admin_update_hardware_clears_assignment_when_not_in_use(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        row = Hardware(
            name="Device",
            brand="Brand",
            status="In Use",
            assigned_to_email="user@test.com",
        )
        db.session.add(row)
        db.session.commit()
        row_id = row.id

    login_admin(client)
    res = client.patch(
        f"/api/admin/hardware/{row_id}",
        json={"status": "Available"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "Available"
    assert data["assignedTo"] is None
