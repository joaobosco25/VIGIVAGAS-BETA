import re
from datetime import datetime, timedelta


def _digits(value: str | None) -> str:
    return re.sub(r"\D", "", value or "")


def mask_cpf(value: str | None) -> str:
    digits = _digits(value)
    if len(digits) != 11:
        return "***.***.***-**" if value else "-"
    return f"***.***.{digits[6:9]}-**"


def mask_cnpj(value: str | None) -> str:
    digits = _digits(value)
    if len(digits) != 14:
        return "**.***.***/****-**" if value else "-"
    return f"**.***.***/{digits[8:12]}-**"


def mask_phone(value: str | None) -> str:
    digits = _digits(value)
    if len(digits) < 8:
        return "****" if value else "-"
    return f"(**) *****-{digits[-4:]}"


def mask_email(value: str | None) -> str:
    email = (value or "").strip()
    if "@" not in email:
        return "***" if email else "-"
    local, domain = email.split("@", 1)
    if not local:
        return f"***@{domain}"
    visible = local[:2] if len(local) >= 2 else local[:1]
    return f"{visible}***@{domain}"


def mask_ip(value: str | None) -> str:
    ip = (value or "").strip()
    if not ip:
        return "-"
    if ":" in ip:
        parts = ip.split(":")
        return ":".join(parts[:2]) + ":****"
    parts = ip.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.***.***"
    return "***"


def retention_cutoff(days: int = 180) -> str:
    return (datetime.utcnow() - timedelta(days=days)).isoformat()
