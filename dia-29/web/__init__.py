# Factory Flask — InvestidorWeb Dia 29

from flask import Flask

from config import MAX_CONTENT_LENGTH, SECRET_KEY
from web.helpers import inject_globals


def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    # Flask resolve paths relativos ao pacote web/ — forcar raiz dia-29
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    app.template_folder = str(root / "templates")
    app.static_folder = str(root / "static")
    app.secret_key = SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    app.context_processor(inject_globals)

    from routes import register_all

    register_all(app)
    return app
