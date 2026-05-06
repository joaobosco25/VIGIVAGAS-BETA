import os
import secrets
import time
from functools import wraps
from flask import abort, current_app, flash, redirect, request, session, url_for

_RATE_BUCKET = {}
_RATE_TABLE_READY = False


def client_ip() -> str:
    # Por padrão, não confia em X-Forwarded-For porque esse header pode ser falsificado.
    # No Render/proxy confiável, habilite TRUST_PROXY=1 ou TRUST_PROXY_HEADERS=1.
    if os.getenv("TRUST_PROXY", os.getenv("TRUST_PROXY_HEADERS", "0")) == "1":
        forwarded = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if forwarded:
            return forwarded
    return request.remote_addr or "0.0.0.0"


def csrf_token() -> str:
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def validate_csrf() -> bool:
    sent = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
    return bool(sent and secrets.compare_digest(sent, session.get("csrf_token", "")))


def _db_rate_limit_enabled() -> bool:
    return os.getenv("RATE_LIMIT_STORAGE", "db").strip().lower() in {"db", "database", "postgres"}


def _ensure_rate_limit_table(conn):
    global _RATE_TABLE_READY
    if _RATE_TABLE_READY:
        return
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS rate_limit_events (
            id SERIAL PRIMARY KEY,
            scope TEXT NOT NULL,
            key_value TEXT NOT NULL,
            created_at DOUBLE PRECISION NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_rate_limit_scope_key_time ON rate_limit_events (scope, key_value, created_at)")
    conn.commit()
    _RATE_TABLE_READY = True


def _is_rate_limited_db(scope: str, limit: int, window_seconds: int) -> bool:
    from utils.db import get_connection
    now = time.time()
    key = client_ip()
    cutoff = now - window_seconds
    conn = get_connection()
    try:
        _ensure_rate_limit_table(conn)
        conn.execute("DELETE FROM rate_limit_events WHERE created_at < ?", (cutoff - 60,))
        row = conn.execute(
            "SELECT COUNT(*) AS total FROM rate_limit_events WHERE scope = ? AND key_value = ? AND created_at >= ?",
            (scope, key, cutoff),
        ).fetchone()
        total = int(row["total"] if row else 0)
        if total >= limit:
            conn.commit()
            return True
        conn.execute("INSERT INTO rate_limit_events (scope, key_value, created_at) VALUES (?, ?, ?)", (scope, key, now))
        conn.commit()
        return False
    finally:
        conn.close()


def _is_rate_limited_memory(scope: str, limit: int, window_seconds: int) -> bool:
    now = time.time()
    key = f"{scope}:{client_ip()}"
    bucket = [t for t in _RATE_BUCKET.get(key, []) if now - t < window_seconds]
    if len(bucket) >= limit:
        _RATE_BUCKET[key] = bucket
        return True
    bucket.append(now)
    _RATE_BUCKET[key] = bucket
    return False


def is_rate_limited(scope: str, limit: int = 10, window_seconds: int = 300) -> bool:
    if _db_rate_limit_enabled():
        try:
            return _is_rate_limited_db(scope, limit, window_seconds)
        except Exception:
            # Fallback defensivo para não derrubar o site se a tabela ainda não existir.
            return _is_rate_limited_memory(scope, limit, window_seconds)
    return _is_rate_limited_memory(scope, limit, window_seconds)


def require_rate_limit(scope: str, limit: int = 10, window_seconds: int = 300):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if is_rate_limited(scope, limit, window_seconds):
                flash("Muitas tentativas em pouco tempo. Aguarde alguns minutos e tente novamente.", "error")
                return redirect(request.referrer or url_for("public.index") if "public.index" in current_app.view_functions else "/")
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def init_security(app):
    @app.context_processor
    def inject_security_helpers():
        return {"csrf_token": csrf_token}

    @app.before_request
    def enforce_csrf_and_basic_rate_limit():
        if request.method == "POST":
            endpoint = request.endpoint or "post"
            if any(term in endpoint for term in ("login", "cadastro", "cadastrar", "validar", "reenviar", "reset", "excluir", "anonimizar", "status", "antifraude")):
                if is_rate_limited(endpoint, limit=8, window_seconds=300):
                    flash("Muitas tentativas em pouco tempo. Aguarde alguns minutos e tente novamente.", "error")
                    return redirect(request.referrer or "/")
            if not validate_csrf():
                flash("Sessão expirada ou formulário inválido. Recarregue a página e tente novamente.", "error")
                return redirect(request.referrer or "/")

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        response.headers.setdefault("Content-Security-Policy", "default-src 'self'; img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com; style-src 'self' https://fonts.googleapis.com; script-src 'self'; connect-src 'self' https://viacep.com.br; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
        if request.is_secure or os.getenv("SESSION_COOKIE_SECURE", "0") == "1":
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response
