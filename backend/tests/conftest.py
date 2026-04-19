import os
import sys
from pathlib import Path

# Before any `import app` (Config reads DATABASE_URL at import time).
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from werkzeug.security import generate_password_hash

sys.path.append(str(Path(__file__).resolve().parents[1]))


@pytest.fixture()
def app():
    os.environ["FLASK_SECRET_KEY"] = "test-secret"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["CORS_ORIGINS"] = "http://localhost:5173"

    from app import create_app
    from app.db import db
    from app.models import User

    app = create_app()
    app.config.update(TESTING=True)

    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = User(
            email="admin@test.com",
            password_hash=generate_password_hash("Admin123!"),
            role="admin",
        )
        user = User(
            email="user@test.com",
            password_hash=generate_password_hash("pass123"),
            role="user",
        )
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
