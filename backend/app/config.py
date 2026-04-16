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

        if not os.path.isabs(extracted):
            extracted = os.path.abspath(os.path.join(repo_root, extracted))

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

