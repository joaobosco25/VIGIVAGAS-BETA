import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from utils.validators import format_cnpj, is_valid_cnpj, only_digits

BRASILAPI_URL = "https://brasilapi.com.br/api/cnpj/v1/{cnpj}"

ACTIVE_VALUES = {
    "ATIVA",
    "ATIVO",
    "02 - ATIVA",
    "2",
    "02",
}


def _normalize_text(value) -> str:
    return str(value or "").strip().upper()


def _is_active(payload: dict) -> bool:
    candidates = [
        payload.get("descricao_situacao_cadastral"),
        payload.get("situacao_cadastral"),
        payload.get("situacao"),
        payload.get("status"),
    ]
    return any(_normalize_text(item) in ACTIVE_VALUES for item in candidates)


def _fallback_allowed() -> bool:
    return os.getenv("CNPJ_ALLOW_FALLBACK_ON_API_ERROR", "1") == "1"


def _fallback_payload(digits: str) -> dict:
    return {
        "cnpj": format_cnpj(digits),
        "razao_social": "VALIDACAO PENDENTE",
        "nome_fantasia": "",
        "situacao_cadastral": "VALIDACAO PENDENTE",
        "municipio": "",
        "uf": "",
        "modo_validacao": "fallback_local",
    }


def consultar_cnpj(cnpj: str) -> tuple[bool, str, dict | None]:
    digits = only_digits(cnpj)
    if not is_valid_cnpj(digits):
        return False, "Informe um CNPJ válido.", None

    url = BRASILAPI_URL.format(cnpj=digits)
    try:
        with urlopen(url, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            return False, "CNPJ não encontrado na base de consulta.", None
        if _fallback_allowed():
            return True, "Validação online do CNPJ indisponível no momento. Cadastro liberado em modo de teste local.", _fallback_payload(digits)
        return False, "Não foi possível validar o CNPJ no momento. Tente novamente em instantes.", None
    except URLError:
        if _fallback_allowed():
            return True, "Validação online do CNPJ indisponível no momento. Cadastro liberado em modo de teste local.", _fallback_payload(digits)
        return False, "Não foi possível consultar o CNPJ no momento. Verifique a conexão e tente novamente.", None
    except Exception:
        if _fallback_allowed():
            return True, "Falha na consulta externa do CNPJ. Cadastro liberado em modo de teste local.", _fallback_payload(digits)
        return False, "Falha inesperada ao validar o CNPJ. Tente novamente.", None

    if not _is_active(payload):
        return False, "O CNPJ informado não está com situação ativa e não pode solicitar cadastro.", payload

    dados = {
        "cnpj": format_cnpj(digits),
        "razao_social": _normalize_text(payload.get("razao_social") or payload.get("descricao_identificador_matriz_filial") or payload.get("nome") or ""),
        "nome_fantasia": _normalize_text(payload.get("nome_fantasia") or payload.get("fantasia") or ""),
        "situacao_cadastral": _normalize_text(
            payload.get("descricao_situacao_cadastral")
            or payload.get("situacao_cadastral")
            or payload.get("situacao")
            or payload.get("status")
            or "ATIVA"
        ),
        "municipio": _normalize_text(payload.get("municipio") or payload.get("cidade_exterior") or ""),
        "uf": _normalize_text(payload.get("uf") or ""),
        "modo_validacao": "online",
    }
    return True, "CNPJ validado com sucesso.", dados
