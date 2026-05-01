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


def _env_bool(name: str, default: str = "1") -> bool:
    return (os.getenv(name, default) or default).strip().lower() in {"1", "true", "sim", "yes", "on"}


def send_email_token(email_destino: str, token: str) -> tuple[bool, str]:
    """Envia código numérico de validação para o e-mail do recrutador.

    O token é um código de 5 dígitos gerado na rota de recrutador e expira em 15 minutos.
    Se SMTP não estiver configurado, salva em database/outbox para teste local.
    """
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_sender = os.getenv("SMTP_FROM", os.getenv("SMTP_SENDER", os.getenv("MAIL_FROM", smtp_user))).strip()
    smtp_tls = _env_bool("SMTP_TLS", os.getenv("SMTP_USE_TLS", "1"))

    subject = "Código de validação do recrutador - VigiVagas"
    body = (
        "Olá!\n\n"
        "Recebemos uma solicitação de cadastro de recrutador no VigiVagas.\n\n"
        f"Seu código de validação é: {token}\n\n"
        "Digite esse código na tela de validação para confirmar seu e-mail.\n"
        "Este código expira em 15 minutos.\n\n"
        "Depois da validação do e-mail, o acesso continuará pendente até a análise do Maurício.\n\n"
        "Se você não solicitou esse cadastro, ignore esta mensagem.\n"
    )

    if smtp_host and smtp_sender:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = smtp_sender
        msg["To"] = email_destino
        msg.set_content(body)
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                if smtp_tls:
                    server.starttls()
                if smtp_user:
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)
            return True, "Código de validação enviado por e-mail. Verifique sua caixa de entrada e o spam."
        except Exception as exc:
            # Em produção, mostramos uma mensagem segura ao usuário e registramos o detalhe no log.
            print(f"[VigiVagas] Falha ao enviar e-mail SMTP para {email_destino}: {exc}")
            return False, "Não foi possível enviar o código por e-mail agora. Confira a configuração SMTP e tente reenviar."

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_email = email_destino.replace("@", "_at_").replace(".", "_")
    file_path = _outbox_dir() / f"{timestamp}_{safe_email}.txt"
    file_path.write_text(
        f"DESTINO: {email_destino}\nASSUNTO: {subject}\n\n{body}",
        encoding="utf-8",
    )
    return True, f"Ambiente local sem SMTP configurado. O código de validação foi salvo em {file_path}."


def send_password_reset_link(email_destino: str, reset_url: str, tipo_usuario: str) -> tuple[bool, str]:
    """Envia link seguro de redefinição de senha."""
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_sender = os.getenv("SMTP_FROM", os.getenv("SMTP_SENDER", os.getenv("MAIL_FROM", smtp_user))).strip()
    smtp_tls = _env_bool("SMTP_TLS", os.getenv("SMTP_USE_TLS", "1"))

    subject = "Redefinição de senha - VigiVagas"
    body = (
        "Olá!\n\n"
        f"Recebemos uma solicitação para redefinir a senha da sua conta de {tipo_usuario} no VigiVagas.\n\n"
        f"Acesse o link abaixo para criar uma nova senha:\n{reset_url}\n\n"
        "Este link expira em 1 hora e só pode ser usado uma vez.\n\n"
        "Se você não solicitou esta alteração, ignore esta mensagem.\n"
    )

    if smtp_host and smtp_sender:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = smtp_sender
        msg["To"] = email_destino
        msg.set_content(body)
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                if smtp_tls:
                    server.starttls()
                if smtp_user:
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)
            return True, "Se o e-mail estiver cadastrado, enviaremos um link de redefinição de senha."
        except Exception as exc:
            print(f"[VigiVagas] Falha ao enviar redefinição de senha para {email_destino}: {exc}")
            return False, "Não foi possível enviar o e-mail agora. Confira a configuração SMTP e tente novamente."

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_email = email_destino.replace("@", "_at_").replace(".", "_")
    file_path = _outbox_dir() / f"{timestamp}_reset_{safe_email}.txt"
    file_path.write_text(
        f"DESTINO: {email_destino}\nASSUNTO: {subject}\n\n{body}",
        encoding="utf-8",
    )
    return True, f"Ambiente local sem SMTP configurado. O link de redefinição foi salvo em {file_path}."
