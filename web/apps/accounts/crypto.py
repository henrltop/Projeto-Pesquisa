"""Helpers para cifrar/decifrar a chave OpenAI do usuario com Fernet (AES-128 + HMAC)."""
from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _fernet() -> Fernet:
    key = getattr(settings, "FIELD_ENCRYPTION_KEY", "")
    if not key:
        raise RuntimeError(
            "FIELD_ENCRYPTION_KEY nao configurado. Gere com: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt(plaintext: str) -> str:
    if not plaintext:
        return ""
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str | None:
    if not ciphertext:
        return None
    try:
        return _fernet().decrypt(ciphertext.encode()).decode()
    except InvalidToken:
        return None


def mask(plaintext: str, keep: int = 4) -> str:
    """Formata uma chave para exibicao (sk-****1234)."""
    if not plaintext:
        return ""
    if len(plaintext) <= keep + 4:
        return "*" * len(plaintext)
    return f"{plaintext[:3]}{'*' * 6}{plaintext[-keep:]}"
