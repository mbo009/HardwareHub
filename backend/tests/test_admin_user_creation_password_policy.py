def login_admin(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "admin@test.com", "password": "Admin123!"},
    )
    assert res.status_code == 200


def test_admin_create_user_requires_auth(client):
    res = client.post(
        "/api/admin/users",
        json={"email": "new@test.com"},
    )
    assert res.status_code == 401


def test_admin_create_user_success_returns_temporary_password(client):
    login_admin(client)
    res = client.post(
        "/api/admin/users",
        json={
            "email": "new5@booksy.com",
            "role": "user",
        },
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["email"] == "new5@booksy.com"
    assert data["role"] == "user"
    assert data["mustChangePassword"] is True
    assert isinstance(data["temporaryPassword"], str)
    assert len(data["temporaryPassword"]) >= 8


def test_admin_create_user_rejects_invalid_role(client):
    login_admin(client)
    res = client.post(
        "/api/admin/users",
        json={"email": "new2@booksy.com", "role": "manager"},
    )
    assert res.status_code == 400
    assert res.get_json()["error"] == "invalid_role"


def test_admin_create_user_rejects_wrong_domain(client):
    login_admin(client)
    res = client.post(
        "/api/admin/users",
        json={"email": "new@other.com"},
    )
    assert res.status_code == 400
    assert res.get_json()["error"] == "invalid_email_domain"


def test_admin_create_user_rejects_duplicate_email(client):
    login_admin(client)
    first = client.post(
        "/api/admin/users",
        json={"email": "new3@booksy.com"},
    )
    assert first.status_code == 201

    res = client.post(
        "/api/admin/users",
        json={"email": "new3@booksy.com"},
    )
    assert res.status_code == 409
    assert res.get_json()["error"] == "email_already_exists"
