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
