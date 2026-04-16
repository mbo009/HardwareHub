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

    db.init_app(app)

    origins = [o.strip() for o in app.config.get("CORS_ORIGINS_RAW", "").split(",") if o.strip()]
    CORS(app, resources={r"/api/*": {"origins": origins}}, supports_credentials=True)

    app.register_blueprint(api_bp)

    @app.get("/")
    def index():
        return {"service": "HardwareHub API"}

    return app

