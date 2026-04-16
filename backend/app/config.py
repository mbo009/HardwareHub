import os


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///backend/instance/hardwarehub.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() in {"1", "true", "yes"}

    CORS_ORIGINS_RAW = os.environ.get("CORS_ORIGINS", "http://localhost:5173")

    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "mock").lower()
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

