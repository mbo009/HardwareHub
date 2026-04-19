from datetime import date
import secrets
import string

from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from app.auth.decorators import admin_required
from app.db import db
from app.hardware.serialization import hardware_public_dict
from app.models import Hardware, User
from app.security import validate_password

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
VALID_HARDWARE_STATUSES = {"Available", "In Use", "Repair", "Unknown"}


def generate_temporary_password(length=12):
    required_sets = [
        string.ascii_uppercase,
        string.ascii_lowercase,
        string.digits,
        "!@#$%^&*()_+-=",
    ]
    chars = [secrets.choice(charset) for charset in required_sets]
    pool = "".join(required_sets)
    while len(chars) < length:
        chars.append(secrets.choice(pool))
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


@admin_bp.post("/users")
@admin_required
def create_user():
    data = request.get_json(silent=True, force=True) or {}

    email = (data.get("email") or "").strip().lower()
    role_raw = data.get("role") or "user"
    if not isinstance(role_raw, str):
        return jsonify({"error": "invalid_role"}), 400
    role = role_raw.strip().lower()

    if role not in {"admin", "user"}:
        return jsonify({"error": "invalid_role"}), 400

    if not email:
        return jsonify({"error": "invalid_email"}), 400

    if not email.endswith("@booksy.com"):
        return jsonify({"error": "invalid_email_domain"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email_already_exists"}), 409

    temporary_password = generate_temporary_password()
    errors = validate_password(temporary_password)
    if errors:
        return jsonify({"error": "temporary_password_generation_failed"}), 500

    user = User(
        email=email,
        password_hash=generate_password_hash(temporary_password),
        role=role,
        must_change_password=True,
    )

    db.session.add(user)
    db.session.commit()

    payload = {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "temporaryPassword": temporary_password,
        "mustChangePassword": user.must_change_password,
    }
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
        serial_number=(data.get("serialNumber") or "").strip() or None,
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
        "serialNumber": hardware.serial_number,
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


@admin_bp.patch("/hardware/<int:hardware_id>/repair")
@admin_required
def mark_hardware_repair(hardware_id):
    hardware = db.session.get(Hardware, hardware_id)
    if not hardware:
        return jsonify({"error": "hardware_not_found"}), 404

    was_in_use = hardware.status == "In Use"

    if was_in_use:
        hardware.assigned_to_email = None
        hardware.status = "Available"
    elif hardware.status == "Repair":
        hardware.status = "Available"
    else:
        hardware.status = "Repair"

    db.session.commit()

    return jsonify(
        {
            "id": hardware.id,
            "status": hardware.status,
            "assignedTo": hardware.assigned_to_email,
            "wasInUse": was_in_use,
        }
    ), 200


@admin_bp.patch("/hardware/<int:hardware_id>")
@admin_required
def update_hardware(hardware_id):
    hardware = db.session.get(Hardware, hardware_id)
    if not hardware:
        return jsonify({"error": "hardware_not_found"}), 404

    data = request.get_json(silent=True) or {}
    allowed_fields = {
        "name",
        "brand",
        "serialNumber",
        "notes",
        "status",
        "assignedTo",
    }
    if not any(field in data for field in allowed_fields):
        return jsonify({"error": "no_fields_to_update"}), 400

    if "name" in data:
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"error": "invalid_name"}), 400
        hardware.name = name

    if "brand" in data:
        brand = (data.get("brand") or "").strip()
        if not brand:
            return jsonify({"error": "invalid_brand"}), 400
        hardware.brand = brand

    if "serialNumber" in data:
        serial = (data.get("serialNumber") or "").strip()
        hardware.serial_number = serial or None

    if "notes" in data:
        notes = data.get("notes")
        if notes is None:
            hardware.notes = None
        elif isinstance(notes, str):
            cleaned = notes.strip()
            hardware.notes = cleaned or None
        else:
            return jsonify({"error": "invalid_notes"}), 400

    final_status = hardware.status
    if "status" in data:
        requested_status = (data.get("status") or "").strip()
        if requested_status not in VALID_HARDWARE_STATUSES:
            return jsonify({"error": "invalid_status"}), 400
        final_status = requested_status

    final_assigned = hardware.assigned_to_email
    if "assignedTo" in data:
        assigned = (data.get("assignedTo") or "").strip().lower()
        final_assigned = assigned or None

    if final_status == "In Use":
        if not final_assigned:
            return jsonify({"error": "assigned_to_required_for_in_use"}), 400
        assigned_user = User.query.filter_by(email=final_assigned).first()
        if not assigned_user:
            return jsonify({"error": "assigned_user_not_found"}), 400
    else:
        if "assignedTo" in data and final_assigned:
            return jsonify({"error": "assigned_to_requires_in_use"}), 400
        final_assigned = None

    hardware.status = final_status
    hardware.assigned_to_email = final_assigned
    db.session.commit()

    return jsonify(hardware_public_dict(hardware)), 200
