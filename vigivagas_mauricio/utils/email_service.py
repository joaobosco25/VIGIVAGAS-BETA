import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

OUTBOX_DIRNAME = "outbox"


def _base_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def _outbox_dir() -> Path:
    path = _base_dir() / "database" / OUTBOX_DIRNAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_validation_link(token: str) -> str:
    base_url = os.getenv("APP_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
    return f"{base_url}/recrutador/validar-email?token={token}"


def send_email_token(email_destino: str, token: str) -> tuple[bool, str]:
    link = build_validation_link(token)
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_sender = os.getenv("SMTP_SENDER", smtp_user).strip()
    smtp_tls = os.getenv("SMTP_TLS", "1") == "1"

    subject = "Validação de e-mail do recrutador - VigiVagas"
    body = (
        "Seu cadastro de recrutador foi recebido.\n\n"
        "Use o link abaixo para validar seu e-mail:\n"
        f"{link}\n\n"
        "Depois da validação do e-mail, o acesso continuará pendente até a análise do Maurício.\n"
    )

    if smtp_host and smtp_sender:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = smtp_sender
        msg["To"] = email_destino
        msg.set_content(body)
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                if smtp_tls:
                    server.starttls()
                if smtp_user:
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)
            return True, "Token de validação enviado por e-mail."
        except Exception:
            pass

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_email = email_destino.replace("@", "_at_").replace(".", "_")
    file_path = _outbox_dir() / f"{timestamp}_{safe_email}.txt"
    file_path.write_text(
        f"DESTINO: {email_destino}\nASSUNTO: {subject}\n\n{body}",
        encoding="utf-8",
    )
    return True, f"Ambiente local sem SMTP configurado. O link de validação foi salvo em {file_path}."
