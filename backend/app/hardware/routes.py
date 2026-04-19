from datetime import date

from flask import Blueprint, jsonify, request, session
from sqlalchemy import and_, case, or_

from app.auth.decorators import login_required
from app.db import db
from app.hardware.serialization import hardware_public_dict, is_pre_arrival
from app.models import Hardware, RentalEvent, User

hardware_bp = Blueprint("hardware", __name__, url_prefix="/api/hardware")


def to_payload(item: Hardware):
    return hardware_public_dict(item)


@hardware_bp.route("/", methods=["GET", "OPTIONS"], strict_slashes=False)
@login_required
def list_hardware():
    status = request.args.get("status", "").strip()
    brand = request.args.get("brand", "").strip()
    search = request.args.get("search", "").strip()
    date_from_raw = request.args.get("dateFrom", "").strip()
    date_to_raw = request.args.get("dateTo", "").strip()
    sort_by = request.args.get("sortBy", "name").strip()
    order = request.args.get("order", "asc").strip().lower()
    page_raw = request.args.get("page", "").strip()
    limit_raw = request.args.get("limit", "").strip()

    query = Hardware.query

    assigned_to_param = (request.args.get("assignedTo") or "").strip().lower()
    if assigned_to_param:
        user_id = session.get("user_id")
        actor = db.session.get(User, user_id) if user_id else None
        if not actor:
            return jsonify({"error": "unauthorized"}), 401
        if assigned_to_param != actor.email.strip().lower():
            return jsonify({"error": "forbidden_assigned_to"}), 403
        query = query.filter(Hardware.assigned_to_email == assigned_to_param)

    if status == "Ordered":
        query = query.filter(
            and_(
                Hardware.purchase_date.isnot(None),
                Hardware.purchase_date > date.today(),
                Hardware.status.in_(["Available", "Unknown"]),
            )
        )
    elif status == "Available":
        query = query.filter(
            Hardware.status == "Available",
            or_(
                Hardware.purchase_date.is_(None),
                Hardware.purchase_date <= date.today(),
            ),
        )
    elif status:
        query = query.filter(Hardware.status == status)

    if brand:
        query = query.filter(Hardware.brand == brand)

    if search:
        like = f"%{search}%"
        query = query.filter(
            (Hardware.name.ilike(like))
            | (Hardware.brand.ilike(like))
        )

    if date_from_raw:
        try:
            date_from = date.fromisoformat(date_from_raw)
        except ValueError:
            return jsonify({"error": "invalid_date_from"}), 400
        query = query.filter(Hardware.purchase_date >= date_from)

    if date_to_raw:
        try:
            date_to = date.fromisoformat(date_to_raw)
        except ValueError:
            return jsonify({"error": "invalid_date_to"}), 400
        query = query.filter(Hardware.purchase_date <= date_to)

    if sort_by == "status":
        status_rank = case(
            (Hardware.status == "Available", 1),
            (Hardware.status == "In Use", 2),
            (Hardware.status == "Repair", 3),
            else_=4,
        )
        if order == "desc":
            query = query.order_by(status_rank.desc(), Hardware.id.desc())
        else:
            query = query.order_by(status_rank.asc(), Hardware.id.asc())
    else:
        sort_map = {
            "name": Hardware.name,
            "brand": Hardware.brand,
            "serialNumber": Hardware.serial_number,
            "purchaseDate": Hardware.purchase_date,
        }
        sort_col = sort_map.get(sort_by, Hardware.name)
        if order == "desc":
            query = query.order_by(
                sort_col.is_(None).asc(),
                sort_col.desc(),
                Hardware.id.desc(),
            )
        else:
            query = query.order_by(
                sort_col.is_(None).asc(),
                sort_col.asc(),
                Hardware.id.asc(),
            )

    try:
        page = int(page_raw or "1")
        limit = int(limit_raw or "20")
    except ValueError:
        return jsonify({"error": "invalid_pagination"}), 400

    if page < 1 or limit < 1 or limit > 100:
        return jsonify({"error": "invalid_pagination"}), 400

    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    total_pages = (total + limit - 1) // limit

    return jsonify(
        {
            "items": [to_payload(item) for item in items],
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": total_pages,
        }
    )


@hardware_bp.post("/<int:hardware_id>/rent")
@login_required
def rent_hardware(hardware_id):
    user_id = session.get("user_id")
    actor = db.session.get(User, user_id) if user_id else None
    if not actor:
        return jsonify({"error": "unauthorized"}), 401

    hardware = db.session.get(Hardware, hardware_id)
    if not hardware:
        return jsonify({"error": "hardware_not_found"}), 404

    if hardware.status != "Available":
        return jsonify({"error": "cannot_rent"}), 409

    if is_pre_arrival(hardware):
        return jsonify({"error": "not_yet_available"}), 409

    prev_status = hardware.status
    hardware.status = "In Use"
    hardware.assigned_to_email = actor.email.strip().lower()

    db.session.add(
        RentalEvent(
            hardware_id=hardware.id,
            actor_user_id=actor.id,
            action="RENT",
            from_status=prev_status,
            to_status="In Use",
        )
    )
    db.session.commit()

    return jsonify(to_payload(hardware)), 200


@hardware_bp.post("/<int:hardware_id>/return")
@login_required
def return_hardware(hardware_id):
    user_id = session.get("user_id")
    actor = db.session.get(User, user_id) if user_id else None
    if not actor:
        return jsonify({"error": "unauthorized"}), 401

    hardware = db.session.get(Hardware, hardware_id)
    if not hardware:
        return jsonify({"error": "hardware_not_found"}), 404

    if hardware.status != "In Use":
        return jsonify({"error": "cannot_return"}), 409

    assigned = (hardware.assigned_to_email or "").strip().lower()
    actor_email = actor.email.strip().lower()
    if not assigned or assigned != actor_email:
        return jsonify({"error": "forbidden_return"}), 403

    prev_status = hardware.status
    hardware.status = "Available"
    hardware.assigned_to_email = None

    db.session.add(
        RentalEvent(
            hardware_id=hardware.id,
            actor_user_id=actor.id,
            action="RETURN",
            from_status=prev_status,
            to_status="Available",
        )
    )
    db.session.commit()

    return jsonify(to_payload(hardware)), 200
