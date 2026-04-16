import os
import sys

from werkzeug.security import generate_password_hash


def main():
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

    from app import create_app
    from app.db import db
    from app.models import User

    app = create_app()

    with app.app_context():
        existing = User.query.count()
        if existing > 0:
            print(f"Users already exist: {existing} records")
            return

        admin = User(
            email="admin@booksy.com",
            password_hash=generate_password_hash("Admin123!"),
            role="admin",
        )
        user = User(
            email="user@booksy.com",
            password_hash=generate_password_hash("User123!"),
            role="user",
        )

        db.session.add(admin)
        db.session.add(user)
        db.session.commit()

        print("Seeded users:")
        print("admin@booksy.com / Admin123!")
        print("user@booksy.com / User123!")


if __name__ == "__main__":
    main()

