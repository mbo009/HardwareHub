from datetime import datetime, timezone

from app.db import db


def utcnow():
    return datetime.now(timezone.utc)


class RentalEvent(db.Model):
    __tablename__ = "rental_events"

    id = db.Column(db.Integer, primary_key=True)
    hardware_id = db.Column(
        db.Integer,
        db.ForeignKey("hardware.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    action = db.Column(db.String(10), nullable=False)
    at = db.Column(db.DateTime, nullable=False, default=utcnow)

    from_status = db.Column(db.String(20), nullable=False)
    to_status = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text, nullable=True)

    hardware = db.relationship("Hardware", back_populates="rental_events")
    actor_user = db.relationship("User", back_populates="rental_events")

    __table_args__ = (
        db.CheckConstraint("action IN ('RENT','RETURN')", name="ck_rental_events_action"),
    )

