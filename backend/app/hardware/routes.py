from datetime import date

from flask import Blueprint, jsonify, request

from app.auth.decorators import login_required
from app.models import Hardware

hardware_bp = Blueprint("hardware", __name__, url_prefix="/api/hardware")


def to_payload(item: Hardware):
    return {
        "id": item.id,
        "seedId": item.seed_id,
        "name": item.name,
        "brand": item.brand,
        "purchaseDate": (
            item.purchase_date.isoformat()
            if item.purchase_date
            else None
        ),
        "status": item.status,
        "assignedTo": item.assigned_to_email,
        "notes": item.notes,
        "history": item.history_text,
    }


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

    if status:
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

    sort_map = {
        "name": Hardware.name,
        "brand": Hardware.brand,
        "purchaseDate": Hardware.purchase_date,
        "status": Hardware.status,
    }
    sort_col = sort_map.get(sort_by, Hardware.name)
    if order == "desc":
        query = query.order_by(sort_col.desc(), Hardware.id.desc())
    else:
        query = query.order_by(sort_col.asc(), Hardware.id.asc())

    if not page_raw and not limit_raw:
        items = query.all()
        return jsonify([to_payload(item) for item in items])

    try:
        page = int(page_raw or "1")
        limit = int(limit_raw or "10")
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
