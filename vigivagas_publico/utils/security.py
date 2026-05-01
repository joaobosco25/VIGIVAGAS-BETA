import os
import secrets
import time
from functools import wraps
from flask import abort, current_app, flash, redirect, request, session, url_for

_RATE_BUCKET = {}


def client_ip() -> str:
    forwarded = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    return forwarded or request.remote_addr or "0.0.0.0"


def csrf_token() -> str:
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def validate_csrf() -> bool:
    sent = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
    return bool(sent and secrets.compare_digest(sent, session.get("csrf_token", "")))


def is_rate_limited(scope: str, limit: int = 10, window_seconds: int = 300) -> bool:
    now = time.time()
    key = f"{scope}:{client_ip()}"
    bucket = [t for t in _RATE_BUCKET.get(key, []) if now - t < window_seconds]
    if len(bucket) >= limit:
        _RATE_BUCKET[key] = bucket
        return True
    bucket.append(now)
    _RATE_BUCKET[key] = bucket
    return False


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
            # Bloqueia repetição excessiva em endpoints sensíveis antes de executar a regra de negócio.
            endpoint = request.endpoint or "post"
            if any(term in endpoint for term in ("login", "cadastro", "cadastrar", "validar", "reenviar", "reset", "excluir")):
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
        response.headers.setdefault("Content-Security-Policy", "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self' https://viacep.com.br; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
        if request.is_secure or os.getenv("SESSION_COOKIE_SECURE", "0") == "1":
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response
