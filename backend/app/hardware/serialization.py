from datetime import date

from app.models import Hardware


def is_pre_arrival(h: Hardware) -> bool:
    d = h.purchase_date
    return bool(d and d > date.today())


def hardware_public_dict(h: Hardware) -> dict:
    return {
        "id": h.id,
        "seedId": h.seed_id,
        "name": h.name,
        "brand": h.brand,
        "serialNumber": h.serial_number,
        "purchaseDate": (
            h.purchase_date.isoformat() if h.purchase_date else None
        ),
        "status": h.status,
        "assignedTo": h.assigned_to_email,
        "notes": h.notes,
        "history": h.history_text,
        "preArrival": is_pre_arrival(h),
    }
