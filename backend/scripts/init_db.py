import os
import sys


def main():
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

    from app import create_app
    from app.db import db

    app = create_app()

    with app.app_context():
        from app import models

        db.create_all()
        db.session.commit()


if __name__ == "__main__":
    main()

