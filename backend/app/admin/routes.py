from datetime import date

from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from app.auth.decorators import admin_required
from app.db import db
from app.models import Hardware, User
from app.security import validate_password

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
VALID_HARDWARE_STATUSES = {"Available", "In Use", "Repair", "Unknown"}


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


@admin_bp.post("/hardware")
@admin_required
def create_hardware():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    brand = (data.get("brand") or "").strip()
    status = (data.get("status") or "Available").strip()
    purchase_date_raw = (data.get("purchaseDate") or "").strip()

    if not name:
        return jsonify({"error": "invalid_name"}), 400

    if not brand:
        return jsonify({"error": "invalid_brand"}), 400

    if status not in VALID_HARDWARE_STATUSES:
        return jsonify({"error": "invalid_status"}), 400

    purchase_date = None
    if purchase_date_raw:
        try:
            purchase_date = date.fromisoformat(purchase_date_raw)
        except ValueError:
            return jsonify({"error": "invalid_purchase_date"}), 400

    hardware = Hardware(
        name=name,
        brand=brand,
        status=status,
        purchase_date=purchase_date,
        assigned_to_email=(data.get("assignedTo") or "").strip() or None,
        notes=data.get("notes"),
        history_text=data.get("history"),
    )
    db.session.add(hardware)
    db.session.commit()

    payload = {
        "id": hardware.id,
        "seedId": hardware.seed_id,
        "name": hardware.name,
        "brand": hardware.brand,
        "purchaseDate": (
            hardware.purchase_date.isoformat()
            if hardware.purchase_date
            else None
        ),
        "status": hardware.status,
        "assignedTo": hardware.assigned_to_email,
        "notes": hardware.notes,
        "history": hardware.history_text,
    }
    return jsonify(payload), 201


@admin_bp.delete("/hardware/<int:hardware_id>")
@admin_required
def delete_hardware(hardware_id):
    hardware = db.session.get(Hardware, hardware_id)
    if not hardware:
        return jsonify({"error": "hardware_not_found"}), 404

    if hardware.status == "In Use":
        return jsonify({"error": "hardware_in_use"}), 409

    db.session.delete(hardware)
    db.session.commit()
    return jsonify({"ok": True}), 200
