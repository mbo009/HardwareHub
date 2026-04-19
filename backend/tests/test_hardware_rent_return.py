from datetime import date

from werkzeug.security import generate_password_hash


def login_user(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "user@test.com", "password": "pass123"},
    )
    assert res.status_code == 200


def test_rent_sets_in_use_and_assigned(client, app):
    from app.db import db
    from app.models import Hardware, RentalEvent

    with app.app_context():
        hw = Hardware(
            name="ThinkPad",
            brand="Lenovo",
            purchase_date=date(2026, 1, 1),
            status="Available",
        )
        db.session.add(hw)
        db.session.commit()
        hw_id = hw.id

    login_user(client)
    res = client.post(f"/api/hardware/{hw_id}/rent")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "In Use"
    assert data["assignedTo"] == "user@test.com"

    with app.app_context():
        ev = RentalEvent.query.filter_by(hardware_id=hw_id).first()
        assert ev is not None
        assert ev.action == "RENT"
        assert ev.from_status == "Available"
        assert ev.to_status == "In Use"


def test_rent_fails_when_not_available(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        hw = Hardware(
            name="ThinkPad",
            brand="Lenovo",
            purchase_date=date(2026, 1, 1),
            status="Repair",
        )
        db.session.add(hw)
        db.session.commit()
        hw_id = hw.id

    login_user(client)
    res = client.post(f"/api/hardware/{hw_id}/rent")
    assert res.status_code == 409
    assert res.get_json()["error"] == "cannot_rent"


def test_return_clears_assignment(client, app):
    from app.db import db
    from app.models import Hardware, RentalEvent

    with app.app_context():
        hw = Hardware(
            name="ThinkPad",
            brand="Lenovo",
            purchase_date=date(2026, 1, 1),
            status="In Use",
            assigned_to_email="user@test.com",
        )
        db.session.add(hw)
        db.session.commit()
        hw_id = hw.id

    login_user(client)
    res = client.post(f"/api/hardware/{hw_id}/return")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "Available"
    assert data["assignedTo"] is None

    with app.app_context():
        ev = (
            RentalEvent.query.filter_by(hardware_id=hw_id, action="RETURN")
            .order_by(RentalEvent.id.desc())
            .first()
        )
        assert ev is not None
        assert ev.from_status == "In Use"
        assert ev.to_status == "Available"


def test_return_forbidden_for_other_users_rental(client, app):
    from app.db import db
    from app.models import Hardware, User

    with app.app_context():
        other = User(
            email="other@booksy.com",
            password_hash=generate_password_hash("Other123!"),
            role="user",
        )
        db.session.add(other)
        hw = Hardware(
            name="ThinkPad",
            brand="Lenovo",
            purchase_date=date(2026, 1, 1),
            status="In Use",
            assigned_to_email="other@booksy.com",
        )
        db.session.add(hw)
        db.session.commit()
        hw_id = hw.id

    login_user(client)
    res = client.post(f"/api/hardware/{hw_id}/return")
    assert res.status_code == 403
    assert res.get_json()["error"] == "forbidden_return"


def test_return_fails_when_not_in_use(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        hw = Hardware(
            name="ThinkPad",
            brand="Lenovo",
            purchase_date=date(2026, 1, 1),
            status="Available",
        )
        db.session.add(hw)
        db.session.commit()
        hw_id = hw.id

    login_user(client)
    res = client.post(f"/api/hardware/{hw_id}/return")
    assert res.status_code == 409
    assert res.get_json()["error"] == "cannot_return"


def test_rent_requires_auth(client, app):
    from app.db import db
    from app.models import Hardware

    with app.app_context():
        hw = Hardware(
            name="ThinkPad",
            brand="Lenovo",
            purchase_date=date(2026, 1, 1),
            status="Available",
        )
        db.session.add(hw)
        db.session.commit()
        hw_id = hw.id

    res = client.post(f"/api/hardware/{hw_id}/rent")
    assert res.status_code == 401
