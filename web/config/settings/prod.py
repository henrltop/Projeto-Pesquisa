from .base import *  # noqa: F401,F403

DEBUG = False

if not SECRET_KEY or SECRET_KEY == "insecure-dev-key-change-me":  # noqa: F405
    raise RuntimeError("DJANGO_SECRET_KEY precisa ser definido em producao.")

if not FIELD_ENCRYPTION_KEY:  # noqa: F405
    raise RuntimeError("FIELD_ENCRYPTION_KEY precisa ser definido em producao.")

if not ALLOWED_HOSTS:  # noqa: F405
    raise RuntimeError("DJANGO_ALLOWED_HOSTS precisa listar os dominios em producao.")

# Django 5 exige a origem confiavel para POST via HTTPS atras do proxy (Nginx),
# senao o login por formulario falha com erro de CSRF. Derivado dos ALLOWED_HOSTS.
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS]  # noqa: F405

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
