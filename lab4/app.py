import os

from src.bootstrap import build_manager
from src.presentation.web_app import create_app


app = create_app(build_manager())


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=int(os.environ.get("PORT", "5000")),
    )
