def test_me_requires_login(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_login_success_sets_session_and_me_works(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "user@test.com", "password": "pass123"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["email"] == "user@test.com"
    assert data["role"] == "user"
    assert data["mustChangePassword"] is False

    res2 = client.get("/api/auth/me")
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2["email"] == "user@test.com"
    assert data2["role"] == "user"
    assert data2["mustChangePassword"] is False


def test_login_rejects_wrong_password(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "user@test.com", "password": "wrong"},
    )
    assert res.status_code == 401


def test_logout_clears_session(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "user@test.com", "password": "pass123"},
    )
    assert res.status_code == 200

    res2 = client.post("/api/auth/logout")
    assert res2.status_code == 200
    assert res2.get_json()["ok"] is True

    res3 = client.get("/api/auth/me")
    assert res3.status_code == 401


def test_login_with_temporary_password_requires_change(client, app):
    from app.db import db
    from app.models import User
    from werkzeug.security import generate_password_hash

    with app.app_context():
        temp_user = User(
            email="temp@test.com",
            password_hash=generate_password_hash("Temp123!"),
            role="user",
            must_change_password=True,
        )
        db.session.add(temp_user)
        db.session.commit()

    login_res = client.post(
        "/api/auth/login",
        json={"email": "temp@test.com", "password": "Temp123!"},
    )
    assert login_res.status_code == 200
    login_data = login_res.get_json()
    assert login_data["mustChangePassword"] is True

    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.get_json()["mustChangePassword"] is True


def test_change_password_clears_must_change_flag(client, app):
    from app.db import db
    from app.models import User
    from werkzeug.security import generate_password_hash

    with app.app_context():
        temp_user = User(
            email="firstlogin@test.com",
            password_hash=generate_password_hash("Temp123!"),
            role="user",
            must_change_password=True,
        )
        db.session.add(temp_user)
        db.session.commit()

    login_res = client.post(
        "/api/auth/login",
        json={"email": "firstlogin@test.com", "password": "Temp123!"},
    )
    assert login_res.status_code == 200
    assert login_res.get_json()["mustChangePassword"] is True

    change_res = client.post(
        "/api/auth/change-password",
        json={"newPassword": "NewStrong123!"},
    )
    assert change_res.status_code == 200
    assert change_res.get_json()["mustChangePassword"] is False

    client.post("/api/auth/logout")

    relogin_old = client.post(
        "/api/auth/login",
        json={"email": "firstlogin@test.com", "password": "Temp123!"},
    )
    assert relogin_old.status_code == 401

    relogin_new = client.post(
        "/api/auth/login",
        json={"email": "firstlogin@test.com", "password": "NewStrong123!"},
    )
    assert relogin_new.status_code == 200
    assert relogin_new.get_json()["mustChangePassword"] is False
