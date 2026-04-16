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

    res2 = client.get("/api/auth/me")
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2["email"] == "user@test.com"
    assert data2["role"] == "user"


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
