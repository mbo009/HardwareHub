from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash

from app.db import db
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.get("/me")
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    user = db.session.get(User, user_id)
    if not user or user.disabled_at is not None:
        session.clear()
        return jsonify({"error": "unauthorized"}), 401

    return jsonify({"email": user.email, "role": user.role})


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "invalid_credentials"}), 401

    user = User.query.filter_by(email=email).first()
    if not user or user.disabled_at is not None:
        return jsonify({"error": "invalid_credentials"}), 401

    if not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid_credentials"}), 401

    session.clear()
    session["user_id"] = user.id

    return jsonify({"email": user.email, "role": user.role})


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})
