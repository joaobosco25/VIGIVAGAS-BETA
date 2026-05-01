import os
from flask import Flask
from dotenv import load_dotenv

from routes.public import public_bp
from routes.recrutador import recrutador_bp
from routes.vigilante import vigilante_bp
from utils.db import init_db
from utils.security import init_security


load_dotenv()


def _must_get_env(name: str) -> str:
    value = (os.getenv(name, "") or "").strip()
    if not value:
        raise RuntimeError(f"Variável obrigatória ausente: {name}")
    return value


def _assert_safe_runtime() -> None:
    secret = _must_get_env("SECRET_KEY")

    if len(secret) < 24 or "troque" in secret.lower():
        raise RuntimeError(
            "SECRET_KEY insegura. Defina uma chave forte antes de subir a aplicação."
        )

    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app_env = (os.getenv("APP_ENV", "production") or "production").strip().lower()

    if app_env in {"beta", "producao", "produção", "production", "prod"} and debug:
        raise RuntimeError("FLASK_DEBUG precisa estar desligado em beta/produção.")

    database_url = _must_get_env("DATABASE_URL")

    if not database_url.lower().startswith(("postgresql://", "postgres://")):
        raise RuntimeError("DATABASE_URL deve apontar para PostgreSQL em ambiente beta.")


def should_run_init_db() -> bool:
    return os.getenv("RUN_INIT_DB", "0").strip() == "1"


def create_app():
    _assert_safe_runtime()

    app = Flask(__name__)

    app.config["SECRET_KEY"] = _must_get_env("SECRET_KEY")
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = os.getenv("SESSION_COOKIE_SECURE", "0") == "1"
    app.config["PERMANENT_SESSION_LIFETIME"] = int(
        os.getenv("SESSION_LIFETIME_SECONDS", "7200")
    )
    app.config["SESSION_COOKIE_NAME"] = os.getenv(
        "SESSION_COOKIE_NAME", "vigivagas_public_session"
    )

    init_security(app)

    app.register_blueprint(public_bp)
    app.register_blueprint(recrutador_bp)
    app.register_blueprint(vigilante_bp)

    @app.after_request
    def add_no_cache_headers(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    if should_run_init_db():
        with app.app_context():
            init_db()

    return app


app = create_app()


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    port = int(os.getenv("PORT", "5000"))
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    app.run(debug=debug, host=host, port=port)
