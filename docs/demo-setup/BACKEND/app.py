import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from extensions import db


def create_app(config_object="config", testing=False):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, ".."))

    app = Flask(
        __name__,
        template_folder=os.path.join(project_root, "FRONTEND", "templates"),
        static_folder=os.path.join(project_root, "FRONTEND", "static"),
    )

    if testing:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SECRET_KEY"] = "test-secret-key"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["SESSION_COOKIE_HTTPONLY"] = True
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        app.config["WTF_CSRF_ENABLED"] = False
    else:
        app.config.from_pyfile(os.path.join(base_dir, "config.py"))

    db.init_app(app)

    with app.app_context():
        from models import init_db
        from routes import register_routes
        register_routes(app)
        if not testing:
            init_db()

    return app


if __name__ == "__main__":
    application = create_app()
    application.run()
