import os
from flask import Flask
from flask_cors import CORS
from sqlalchemy import text

from .admin import admin_bp
from .hardware import hardware_bp
from .config import Config
from .auth import auth_bp
from .db import db
from .routes import api_bp


def ensure_sqlite_schema_compat(app):
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if not db_uri.startswith("sqlite:///"):
        return

    with app.app_context():
        conn = db.engine.connect()
        try:
            result = conn.execute(text("PRAGMA table_info(hardware)"))
            columns = {row[1] for row in result.fetchall()}

            if "serial_number" not in columns:
                conn.execute(
                    text("ALTER TABLE hardware ADD COLUMN serial_number VARCHAR(255)")
                )
                conn.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS "
                        "ix_hardware_serial_number ON hardware (serial_number)"
                    )
                )
                conn.commit()
        finally:
            conn.close()


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    os.makedirs(app.instance_path, exist_ok=True)

    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")

    if db_uri.startswith("sqlite:///"):
        db_path = db_uri[len("sqlite:///") :]
        db_dir = os.path.dirname(db_path)

        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    db.init_app(app)
    ensure_sqlite_schema_compat(app)

    origins = [
        origin.strip()
        for origin in app.config.get("CORS_ORIGINS_RAW", "").split(",")
        if origin.strip()
    ]

    CORS(app, resources={r"/api/*": {"origins": origins}}, supports_credentials=True)

    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(hardware_bp)

    @app.get("/")
    def index():
        return {"service": "HardwareHub API"}

    return app

