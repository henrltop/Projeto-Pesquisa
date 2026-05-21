import os

from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# SQLite para desenvolvimento rapido sem dependencia de Postgres.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Chave Fernet de fallback (SOMENTE dev, nao usar em producao).
# Fernet exige 32 bytes codificados em url-safe base64 (44 chars terminando em "=").
_DEV_FALLBACK_FERNET = "8Y669IJrBj_ibpNe3TlSXByEISlUiaj2aXa4LHBZ8-s="


def _fernet_valido(k: str) -> bool:
    try:
        from cryptography.fernet import Fernet
        Fernet((k or "").encode())
        return True
    except Exception:
        return False


if not _fernet_valido(FIELD_ENCRYPTION_KEY):  # noqa: F405
    FIELD_ENCRYPTION_KEY = _DEV_FALLBACK_FERNET

# Sem Redis em dev: dispatcher usa thread local, broker em memoria para evitar erros.
if not os.environ.get("REDIS_URL"):
    os.environ.setdefault("CELERY_EAGER", "1")
    CELERY_BROKER_URL = "memory://"
    CELERY_RESULT_BACKEND = "cache+memory://"
