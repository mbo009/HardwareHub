import os


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    default_db_path = os.path.abspath(
        os.path.join(repo_root, "backend", "instance", "hardwarehub.db")
    )
    env_db_uri = os.environ.get("DATABASE_URL")

    if env_db_uri and env_db_uri.startswith("sqlite:///"):
        extracted = env_db_uri[len("sqlite:///") :]

        if extracted == ":memory:":
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        elif not os.path.isabs(extracted):
            extracted = os.path.abspath(os.path.join(repo_root, extracted))

        if extracted != ":memory:":
            resolved_db_path = extracted
            SQLALCHEMY_DATABASE_URI = "sqlite:///" + resolved_db_path.replace("\\", "/")
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + default_db_path.replace("\\", "/")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = (
        os.environ.get("SESSION_COOKIE_SECURE", "false").lower()
        in {"1", "true", "yes"}
    )

    CORS_ORIGINS_RAW = os.environ.get("CORS_ORIGINS", "http://localhost:5173")

    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "mock").lower()
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get(
        "GOOGLE_API_KEY", ""
    )
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-001")

    OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:8b")
    OLLAMA_IMAGE_MODE = os.environ.get("OLLAMA_IMAGE_MODE", "auto").lower()


def refresh_llm_config_from_env(app) -> None:
    key = os.environ.get("OPENAI_API_KEY") or app.config.get("OPENAI_API_KEY") or ""
    key = key.strip().strip('"').strip("'").lstrip("\ufeff")
    app.config["OPENAI_API_KEY"] = key
    gkey = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    gkey = gkey.strip().strip('"').strip("'").lstrip("\ufeff")
    app.config["GEMINI_API_KEY"] = gkey
    prov = os.environ.get("LLM_PROVIDER") or app.config.get("LLM_PROVIDER") or "mock"
    app.config["LLM_PROVIDER"] = str(prov).lower().strip().lstrip("\ufeff")
    model = os.environ.get("OPENAI_MODEL") or app.config.get("OPENAI_MODEL") or "gpt-4o-mini"
    app.config["OPENAI_MODEL"] = str(model).strip()
    gmodel = os.environ.get("GEMINI_MODEL") or app.config.get("GEMINI_MODEL") or "gemini-2.0-flash-001"
    app.config["GEMINI_MODEL"] = str(gmodel).strip()
    obase = os.environ.get("OLLAMA_BASE_URL") or app.config.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434"
    app.config["OLLAMA_BASE_URL"] = str(obase).strip().rstrip("/")
    omodel = os.environ.get("OLLAMA_MODEL") or app.config.get("OLLAMA_MODEL") or "qwen3:8b"
    app.config["OLLAMA_MODEL"] = str(omodel).strip()
    oim = os.environ.get("OLLAMA_IMAGE_MODE") or app.config.get("OLLAMA_IMAGE_MODE") or "auto"
    app.config["OLLAMA_IMAGE_MODE"] = str(oim).lower().strip()

