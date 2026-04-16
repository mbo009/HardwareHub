def login_admin(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "admin@test.com", "password": "Admin123!"},
    )
    assert res.status_code == 200


def test_admin_create_user_requires_auth(client):
    res = client.post(
        "/api/admin/users",
        json={"email": "new@test.com", "password": "GoodPass123!"},
    )
    assert res.status_code == 401


def test_admin_create_user_password_too_short(client):
    login_admin(client)
    res = client.post(
        "/api/admin/users",
        json={"email": "new1@test.com", "password": "A1!a"},
    )
    assert res.status_code == 400
    data = res.get_json()
    assert data["error"] == "invalid_password"
    assert "passwordTooShort" in data["details"]


def test_admin_create_user_password_missing_upper(client):
    login_admin(client)
    res = client.post(
        "/api/admin/users",
        json={"email": "new2@test.com", "password": "goodpass123!"},
    )
    assert res.status_code == 400
    assert "passwordWithoutUpper" in res.get_json()["details"]


def test_admin_create_user_password_missing_digits(client):
    login_admin(client)
    res = client.post(
        "/api/admin/users",
        json={"email": "new3@test.com", "password": "GoodPass!!!"},
    )
    assert res.status_code == 400
    assert "passwordWithoutDigits" in res.get_json()["details"]


def test_admin_create_user_password_missing_special(client):
    login_admin(client)
    res = client.post(
        "/api/admin/users",
        json={"email": "new4@test.com", "password": "GoodPass123"},
    )
    assert res.status_code == 400
    assert "passwordWithoutSpecial" in res.get_json()["details"]


def test_admin_create_user_success(client):
    login_admin(client)
    res = client.post(
        "/api/admin/users",
        json={
            "email": "new5@test.com",
            "password": "GoodPass123!",
            "role": "user",
        },
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["email"] == "new5@test.com"
    assert data["role"] == "user"
