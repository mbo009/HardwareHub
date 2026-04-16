from functools import wraps

from flask import jsonify, request, session

from app.db import db
from app.models import User


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            return "", 200

        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "unauthorized"}), 401

        user = db.session.get(User, user_id)
        if not user:
            session.clear()
            return jsonify({"error": "unauthorized"}), 401

        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            return "", 200

        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "unauthorized"}), 401

        user = db.session.get(User, user_id)
        if not user:
            session.clear()
            return jsonify({"error": "unauthorized"}), 401

        if user.role != "admin":
            return jsonify({"error": "forbidden"}), 403

        return fn(*args, **kwargs)

    return wrapper
