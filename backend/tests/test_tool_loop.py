from app.assistant.tool_loop import run_assistant_with_tools


def test_tool_loop_malformed_json_returns_graceful_message(monkeypatch):
    def fake_raw(*_args, **_kwargs):
        return '{"message":"oops" "tool_calls":[]}'

    monkeypatch.setattr(
        "app.assistant.llm_client.complete_assistant_json_raw",
        fake_raw,
    )
    out = run_assistant_with_tools(
        [{"role": "user", "content": "how many macbooks?"}],
        None,
        provider="ollama",
        api_key="",
        model="llava:7b",
        ollama_base_url="http://127.0.0.1:11434",
        ollama_image_mode="auto",
    )
    assert out["proposal"] is None
    assert "could not parse" in (out["message"] or "").lower()
