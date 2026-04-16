from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from app.auth.decorators import admin_required
from app.db import db
from app.models import User
from app.security import validate_password

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.post("/users")
@admin_required
def create_user():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    role = (data.get("role") or "user").strip().lower()

    if role not in {"admin", "user"}:
        return jsonify({"error": "invalid_role"}), 400

    if not email:
        return jsonify({"error": "invalid_email"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email_already_exists"}), 409

    errors = validate_password(password)
    if errors:
        return jsonify({"error": "invalid_password", "details": errors}), 400

    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
    )

    db.session.add(user)
    db.session.commit()

    payload = {"id": user.id, "email": user.email, "role": user.role}
    return jsonify(payload), 201
