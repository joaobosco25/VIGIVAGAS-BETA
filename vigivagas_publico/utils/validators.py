import re
from datetime import datetime


def only_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def normalize_upper(value: str) -> str:
    return (value or "").strip().upper()


def normalize_email(value: str) -> str:
    return (value or "").strip().lower()


def normalize_textarea_upper(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip()).upper()


def format_cpf(value: str) -> str:
    digits = only_digits(value)
    if len(digits) != 11:
        return digits
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


def format_cep(value: str) -> str:
    digits = only_digits(value)
    if len(digits) != 8:
        return digits
    return f"{digits[:5]}-{digits[5:]}"




def format_cnpj(value: str) -> str:
    digits = only_digits(value)
    if len(digits) != 14:
        return digits
    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"


def is_valid_cnpj(value: str) -> bool:
    cnpj = only_digits(value)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    def calc_digit(base: str, weights: list[int]) -> int:
        total = sum(int(d) * w for d, w in zip(base, weights))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    first = calc_digit(cnpj[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    second = calc_digit(cnpj[:12] + str(first), [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return cnpj[-2:] == f"{first}{second}"

def format_phone(value: str) -> str:
    digits = only_digits(value)
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return digits


def is_valid_cpf(value: str) -> bool:
    cpf = only_digits(value)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    total = sum(int(cpf[i]) * (10 - i) for i in range(9))
    first_digit = (total * 10 % 11) % 10
    if first_digit != int(cpf[9]):
        return False

    total = sum(int(cpf[i]) * (11 - i) for i in range(10))
    second_digit = (total * 10 % 11) % 10
    return second_digit == int(cpf[10])


def is_valid_cep(value: str) -> bool:
    return len(only_digits(value)) == 8


def is_valid_phone(value: str) -> bool:
    digits = only_digits(value)
    if len(digits) not in (10, 11):
        return False
    ddd = digits[:2]
    if ddd[0] == '0' or ddd[1] == '0':
        return False
    if len(digits) == 11 and digits[2] != '9':
        return False
    if is_obviously_fake_sequence(digits[-8:]):
        return False
    return True


def is_strong_password(value: str) -> bool:
    if len(value or "") < 10:
        return False
    if not re.search(r"[A-Z]", value):
        return False
    if not re.search(r"[a-z]", value):
        return False
    if not re.search(r"\d", value):
        return False
    if not re.search(r"[^A-Za-z0-9]", value):
        return False
    return True


def validate_vigilante_requirements(curso: str, reciclagem: str) -> tuple[bool, str]:
    curso_norm = normalize_upper(curso)
    reciclagem_norm = normalize_upper(reciclagem)

    if not curso_norm:
        return False, "Informe a situação do curso de vigilante."
    if not reciclagem_norm:
        return False, "Informe a situação da reciclagem."

    opcoes_validas = {"SIM", "NAO", "NÃO", "EM ANDAMENTO"}

    if curso_norm not in opcoes_validas:
        return False, "Selecione uma opção válida para o curso de vigilante."
    if reciclagem_norm not in opcoes_validas:
        return False, "Selecione uma opção válida para a reciclagem."

    return True, ""


def is_obviously_fake_sequence(value: str) -> bool:
    digits = only_digits(value)
    if not digits:
        return False
    if digits == digits[0] * len(digits):
        return True
    sequences = ["0123456789", "1234567890", "9876543210", "0987654321"]
    return any(digits in seq for seq in sequences)


def has_meaningful_length(value: str, minimum: int = 8) -> bool:
    return len(re.sub(r"\s+", " ", (value or "").strip())) >= minimum


VALID_STATE_CODES = {"AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"}


def is_valid_state_code(value: str) -> bool:
    return normalize_upper(value) in VALID_STATE_CODES
