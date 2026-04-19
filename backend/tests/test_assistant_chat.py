def login_user(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "user@test.com", "password": "pass123"},
    )
    assert res.status_code == 200


def test_assistant_chat_requires_auth(client):
    res = client.post("/api/assistant/chat", json={"messages": [{"role": "user", "content": "hi"}]})
    assert res.status_code == 401


def test_assistant_settings_requires_auth(client):
    res = client.get("/api/assistant/settings")
    assert res.status_code == 401


def test_assistant_settings_ollama_text_model_no_vision(client, app, monkeypatch):
    monkeypatch.setattr("app.assistant.routes.load_dotenv", lambda *_a, **_k: None)
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen3:8b")
    monkeypatch.setenv("OLLAMA_IMAGE_MODE", "auto")
    login_user(client)
    res = client.get("/api/assistant/settings")
    assert res.status_code == 200
    data = res.get_json()
    assert data["provider"] == "ollama"
    assert data["model"] == "qwen3:8b"
    assert data["imagesSupported"] is False
    assert data["ollamaImageMode"] == "auto"


def test_assistant_settings_ollama_vision_model(client, app, monkeypatch):
    monkeypatch.setattr("app.assistant.routes.load_dotenv", lambda *_a, **_k: None)
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "llava:7b")
    monkeypatch.setenv("OLLAMA_IMAGE_MODE", "auto")
    login_user(client)
    res = client.get("/api/assistant/settings")
    assert res.status_code == 200
    assert res.get_json()["imagesSupported"] is True


def test_assistant_chat_mock_returns_unavailable(client, app, monkeypatch):
    monkeypatch.setattr("app.assistant.routes.load_dotenv", lambda *_a, **_k: None)
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    login_user(client)
    res = client.post(
        "/api/assistant/chat",
        json={"messages": [{"role": "user", "content": "I have an iPhone 15 for inventory"}]},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("proposal") is None
    assert "unavailable" in (data.get("message") or "").lower()


def test_assistant_chat_gemini_without_key_returns_unavailable(client, app, monkeypatch):
    monkeypatch.setattr("app.assistant.routes.load_dotenv", lambda *_a, **_k: None)
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    login_user(client)
    res = client.post(
        "/api/assistant/chat",
        json={"messages": [{"role": "user", "content": "I have an iPhone 15 for inventory"}]},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("proposal") is None
    assert "unavailable" in (data.get("message") or "").lower()


def test_assistant_chat_rejects_bad_payload(client, app):
    login_user(client)
    res = client.post("/api/assistant/chat", json={"messages": []})
    assert res.status_code == 400


def test_assistant_chat_stock_query_uses_db_not_llm(client, app, monkeypatch):
    """Brand keyword + stock phrasing hits deterministic path (no hallucinated counts)."""
    from datetime import date

    from app.db import db
    from app.models import Hardware

    monkeypatch.setattr("app.assistant.routes.load_dotenv", lambda *_a, **_k: None)
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    with app.app_context():
        db.session.add(
            Hardware(
                name="Dell XPS 15 9510",
                brand="Dell",
                purchase_date=date(2022, 3, 15),
                status="Available",
            )
        )
        db.session.commit()
    login_user(client)
    res = client.post(
        "/api/assistant/chat",
        json={
            "messages": [
                {"role": "user", "content": "how many dell brand stuff we have"},
            ]
        },
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("proposal") is None
    msg = data.get("message") or ""
    assert "Exact database matches" in msg
    assert "1 device(s)" in msg
    assert "Dell XPS 15" in msg


def test_assistant_chat_sony_brand_hits_deterministic_path(client, app, monkeypatch):
    from datetime import date

    from app.db import db
    from app.models import Hardware

    monkeypatch.setattr("app.assistant.routes.load_dotenv", lambda *_a, **_k: None)
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    with app.app_context():
        db.session.add(
            Hardware(
                name="Sony WH-1000XM4",
                brand="Sony",
                purchase_date=date(2023, 1, 10),
                status="In Use",
            )
        )
        db.session.commit()
    login_user(client)
    res = client.post(
        "/api/assistant/chat",
        json={
            "messages": [
                {"role": "user", "content": "okay and how many sony devices do we have"},
            ]
        },
    )
    assert res.status_code == 200
    data = res.get_json()
    msg = data.get("message") or ""
    assert "1 device(s)" in msg
    assert "Sony" in msg
    assert "WH-1000XM4" in msg or "Sony WH" in msg
