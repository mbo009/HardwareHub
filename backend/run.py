import os
import sys

from dotenv import load_dotenv


sys.path.append(os.path.join(os.path.dirname(__file__)))

_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(_repo_root, ".env"), override=True)
load_dotenv()

from app import create_app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "1").lower() in {"1", "true", "yes"}
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)

