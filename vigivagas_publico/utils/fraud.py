from __future__ import annotations

from flask import Request

from utils.validators import normalize_email, normalize_upper, only_digits

DISPOSABLE_EMAIL_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "10minutemail.com", "temp-mail.org",
    "tempmail.com", "yopmail.com", "sharklasers.com", "getnada.com", "trashmail.com",
    "maildrop.cc", "dispostable.com", "fakeinbox.com", "mintemail.com", "mailnesia.com",
}

GENERIC_EMAIL_DOMAINS = {
    "gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "icloud.com", "uol.com.br",
    "bol.com.br", "live.com", "terra.com.br",
}

TEST_WORDS = {
    "TESTE", "TEST", "AAA", "XXXX", "ASD", "QWE", "ADMIN", "USUARIO", "USUÁRIO",
    "NOME", "SEM NOME", "EMPRESA TESTE", "EMPRESA", "FULANO", "BELTRANO",
}


def get_client_ip(req: Request) -> str:
    forwarded = (req.headers.get("X-Forwarded-For") or "").strip()
    if forwarded:
        return forwarded.split(",")[0].strip()[:64]
    return (req.remote_addr or "").strip()[:64]



def get_user_agent(req: Request) -> str:
    return (req.headers.get("User-Agent") or "").strip()[:255]



def email_domain(email: str) -> str:
    email_norm = normalize_email(email)
    return email_norm.split("@", 1)[1] if "@" in email_norm else ""



def is_disposable_email(email: str) -> bool:
    return email_domain(email) in DISPOSABLE_EMAIL_DOMAINS



def is_generic_email(email: str) -> bool:
    return email_domain(email) in GENERIC_EMAIL_DOMAINS



def looks_like_test_name(value: str) -> bool:
    text = normalize_upper(value)
    if not text:
        return True
    if text in TEST_WORDS:
        return True
    compact = text.replace(" ", "")
    if compact in {"AAA", "AAAA", "XXXX", "XXXXX", "TESTE", "TEST"}:
        return True
    if len(compact) < 6:
        return True
    if text.count(" ") < 1:
        return True
    parts = [p for p in text.split() if p]
    if len(parts) < 2:
        return True
    if any(len(p) < 2 for p in parts[:2]):
        return True
    return False



def looks_like_test_company(value: str) -> bool:
    text = normalize_upper(value)
    if not text or text in TEST_WORDS:
        return True
    compact = text.replace(" ", "")
    if len(compact) < 5:
        return True
    return False



def evaluate_vigilante_risk(conn, nome: str, email: str, telefone: str, client_ip: str, user_agent: str) -> tuple[int, str, str]:
    flags: list[str] = []
    if looks_like_test_name(nome):
        flags.append("nome_suspeito")
    if is_disposable_email(email):
        flags.append("email_descartavel")
    phone_digits = only_digits(telefone)
    phone_dup = conn.execute(
        "SELECT COUNT(*) AS total FROM vigilantes WHERE telefone = ? UNION ALL SELECT COUNT(*) AS total FROM candidatos WHERE telefone = ?",
        (telefone, telefone),
    ).fetchall()
    total_phone = sum(int(row["total"] or 0) for row in phone_dup)
    if total_phone >= 1:
        flags.append("telefone_repetido")
    if client_ip:
        ip_dup = conn.execute(
            "SELECT COUNT(*) AS total FROM vigilantes WHERE ip_cadastro = ? UNION ALL SELECT COUNT(*) AS total FROM candidatos WHERE ip_cadastro = ? UNION ALL SELECT COUNT(*) AS total FROM recrutadores WHERE ip_cadastro = ?",
            (client_ip, client_ip, client_ip),
        ).fetchall()
        total_ip = sum(int(row["total"] or 0) for row in ip_dup)
        if total_ip >= 2:
            flags.append("ip_reincidente")
    ua = (user_agent or "").lower()
    if not user_agent or any(bot in ua for bot in ["python", "curl", "bot", "spider", "crawler"]):
        flags.append("agente_suspeito")
    if phone_digits and len(set(phone_digits[-8:])) == 1:
        flags.append("telefone_pouco_confiavel")

    score = len(flags)
    status = "suspeito" if score >= 2 else "normal"
    return score, ", ".join(flags), status



def evaluate_recrutador_risk(conn, nome_empresa: str, nome_responsavel: str, email: str, telefone: str, cnpj: str, client_ip: str, user_agent: str) -> tuple[int, str, str]:
    flags: list[str] = []
    if looks_like_test_company(nome_empresa):
        flags.append("empresa_suspeita")
    if looks_like_test_name(nome_responsavel):
        flags.append("responsavel_suspeito")
    if is_disposable_email(email):
        flags.append("email_descartavel")
    if is_generic_email(email):
        flags.append("email_generico")
    phone_dup = conn.execute(
        "SELECT COUNT(*) AS total FROM recrutadores WHERE telefone = ? UNION ALL SELECT COUNT(*) AS total FROM vigilantes WHERE telefone = ?",
        (telefone, telefone),
    ).fetchall()
    total_phone = sum(int(row["total"] or 0) for row in phone_dup)
    if total_phone >= 1:
        flags.append("telefone_repetido")
    cnpj_dup = conn.execute("SELECT COUNT(*) AS total FROM recrutadores WHERE cnpj = ?", (cnpj,)).fetchone()
    if cnpj_dup and int(cnpj_dup["total"] or 0) >= 1:
        flags.append("cnpj_ja_cadastrado")
    if client_ip:
        ip_dup = conn.execute(
            "SELECT COUNT(*) AS total FROM recrutadores WHERE ip_cadastro = ? UNION ALL SELECT COUNT(*) AS total FROM vigilantes WHERE ip_cadastro = ?",
            (client_ip, client_ip),
        ).fetchall()
        total_ip = sum(int(row["total"] or 0) for row in ip_dup)
        if total_ip >= 2:
            flags.append("ip_reincidente")
    ua = (user_agent or "").lower()
    if not user_agent or any(bot in ua for bot in ["python", "curl", "bot", "spider", "crawler"]):
        flags.append("agente_suspeito")

    score = len(flags)
    status = "suspeito" if score >= 2 else "normal"
    return score, ", ".join(flags), status
