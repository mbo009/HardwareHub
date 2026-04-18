from datetime import datetime, timezone

from app.db import db


def utcnow():
    return datetime.now(timezone.utc)


class Hardware(db.Model):
    __tablename__ = "hardware"

    id = db.Column(db.Integer, primary_key=True)
    seed_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(255), nullable=False, default="")
    serial_number = db.Column(db.String(255), nullable=True, index=True)
    purchase_date = db.Column(db.Date, nullable=True, index=True)
    status = db.Column(db.String(20), nullable=False, index=True)
    assigned_to_email = db.Column(db.String(255), nullable=True, index=True)

    notes = db.Column(db.Text, nullable=True)
    history_text = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )

    rental_events = db.relationship(
        "RentalEvent",
        back_populates="hardware",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('Available','In Use','Repair','Unknown')",
            name="ck_hardware_status",
        ),
    )

