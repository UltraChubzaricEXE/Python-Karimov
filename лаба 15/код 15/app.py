"""Приложение Flask авиакомпании (ЛР15, вариант 8). Application Factory."""
import os

from flask import Flask

from database import close_db, init_db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["DATABASE"] = os.getenv(
        "DATABASE", os.path.join(os.path.dirname(__file__), "airlines.db"))
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    app.teardown_appcontext(close_db)

    from routes_web import web_bp
    from routes_api import api_bp
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    # Инициализация БД при первом обращении
    @app.before_request
    def ensure_db():
        db_path = app.config["DATABASE"]
        if not os.path.exists(db_path):
            init_db(app)

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("404.html"), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)