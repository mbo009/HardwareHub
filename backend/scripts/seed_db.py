import json
import os
import sys
from datetime import datetime


def normalize_status(raw_status):
    value = (raw_status or "").strip()
    if value in {"Available", "In Use", "Repair"}:
        return value
    return "Unknown"


def normalize_purchase_date(raw_date):
    if raw_date is None:
        return None
    if not isinstance(raw_date, str):
        return None
    value = raw_date.strip()
    if not value or value.lower() == "null":
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    return None


def main():
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

    from app import create_app
    from app.db import db
    from app.models import Hardware

    app = create_app()

    seed_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "app",
        "seed",
        "seed_data.json",
    )

    with app.app_context():
        existing = Hardware.query.count()

        if existing > 0:
            print(f"Hardware already seeded: {existing} records")
            return

        with open(seed_path, "r", encoding="utf-8") as f:
            items = json.load(f)

        status_counts = {"Available": 0, "In Use": 0, "Repair": 0, "Unknown": 0}
        invalid_dates = 0

        for item in items:
            seed_id = item.get("id")
            status = normalize_status(item.get("status"))
            purchase_date = normalize_purchase_date(item.get("purchaseDate"))

            if item.get("purchaseDate") is not None and purchase_date is None:
                invalid_dates += 1

            assigned_to_email = None

            if status == "In Use":
                assigned_to_email = item.get("assignedTo") or None

            history_text = item.get("history") or None
            notes = item.get("notes") or None

            hardware = Hardware(
                seed_id=seed_id,
                name=item.get("name") or "",
                brand=item.get("brand") or "",
                serial_number=(item.get("serialNumber") or None),
                purchase_date=purchase_date,
                status=status,
                assigned_to_email=assigned_to_email,
                notes=notes,
                history_text=history_text,
            )
            db.session.add(hardware)
            status_counts[status] += 1

        db.session.commit()

        final_count = Hardware.query.count()
        print(f"Seed imported into hardware: {final_count} records")
        print(f"Status distribution: {status_counts}")
        print(f"Invalid purchaseDate values: {invalid_dates}")


if __name__ == "__main__":
    main()

