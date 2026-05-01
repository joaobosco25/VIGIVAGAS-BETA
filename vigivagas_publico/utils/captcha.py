from random import randint
from flask import session


def generate_captcha(form_key: str) -> str:
    a = randint(1, 9)
    b = randint(1, 9)
    session[f"captcha_answer_{form_key}"] = str(a + b)
    return f"Quanto é {a} + {b}?"



def verify_captcha(form_key: str, user_answer: str) -> bool:
    expected = str(session.get(f"captcha_answer_{form_key}", "")).strip()
    informed = str(user_answer or "").strip()
    session.pop(f"captcha_answer_{form_key}", None)
    return bool(expected) and informed == expected
