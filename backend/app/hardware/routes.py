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
    search = request.args.get("search", "").strip()
    sort_by = request.args.get("sortBy", "name").strip()
    order = request.args.get("order", "asc").strip().lower()

    query = Hardware.query

    if status:
        query = query.filter(Hardware.status == status)

    if search:
        like = f"%{search}%"
        query = query.filter(
            (Hardware.name.ilike(like))
            | (Hardware.brand.ilike(like))
        )

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

    items = query.all()
    return jsonify([to_payload(item) for item in items])
