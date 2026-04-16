import os
import sys

from dotenv import load_dotenv


sys.path.append(os.path.join(os.path.dirname(__file__)))

load_dotenv()

from app import create_app  # noqa: E402


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "1") == "1")

