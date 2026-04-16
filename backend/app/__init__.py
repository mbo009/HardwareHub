import os
from flask import Flask
from flask_cors import CORS

from .config import Config
from .db import db
from .routes import api_bp


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

    origins = [
        origin.strip()
        for origin in app.config.get("CORS_ORIGINS_RAW", "").split(",")
        if origin.strip()
    ]

    CORS(app, resources={r"/api/*": {"origins": origins}}, supports_credentials=True)

    app.register_blueprint(api_bp)

    @app.get("/")
    def index():
        return {"service": "HardwareHub API"}

    return app

