"""Configuracoes comuns (dev e prod). Valores sensiveis vem de variaveis de ambiente."""
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "insecure-dev-key-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_htmx",
    "django_extensions",
    "apps.core",
    "apps.accounts",
    "apps.searches",
    "apps.documents",
    "apps.reviews",
    "apps.validations",
    "apps.dashboard",
    "apps.public",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "iomat"),
        "USER": os.environ.get("POSTGRES_USER", "iomat"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Cuiaba"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "public:home"

# Celery
CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 60 * 60 * 4  # 4h hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 60 * 60 * 3  # 3h soft limit

# Criptografia de campos sensiveis (chave OpenAI dos usuarios)
FIELD_ENCRYPTION_KEY = os.environ.get("FIELD_ENCRYPTION_KEY", "")

# ---------------- Preco do modelo de classificacao ----------------
# USD por 1 milhao de tokens. Valores oficiais do gpt-5.4-mini (jun/2026):
# input $0.75, output $4.50, input cacheado $0.075 por 1M. Usado para a
# estimativa de custo exibida no painel.
OPENAI_PRECO_INPUT_POR_1M = os.environ.get("OPENAI_PRECO_INPUT_POR_1M", "0.75")
OPENAI_PRECO_OUTPUT_POR_1M = os.environ.get("OPENAI_PRECO_OUTPUT_POR_1M", "4.50")

# ---------------- Delimitador de atos (LLM local / OpenWebUI) ----------------
# Fase 1 do pipeline opcional de contexto: um modelo local (gpt-oss:20b) decide
# quais paginas vizinhas pertencem ao mesmo ato, antes da classificacao pelo GPT.
# Pode ser sobrescrito por variaveis de ambiente.
DELIMITADOR_BASE_URL = os.environ.get(
    "DELIMITADOR_BASE_URL", "https://tutoria.cba.ifmt.edu.br"
)
DELIMITADOR_API_KEY = os.environ.get(
    "DELIMITADOR_API_KEY", "sk-a41a6dfea7f041ecb78e3f44fa97dc40"
)
DELIMITADOR_MODELO = os.environ.get("DELIMITADOR_MODELO", "gpt-oss:20b")
DELIMITADOR_VERIFY_SSL = os.environ.get("DELIMITADOR_VERIFY_SSL", "False").lower() == "true"
# Janela de paginas vizinhas (cada lado) oferecidas ao delimitador.
DELIMITADOR_JANELA = int(os.environ.get("DELIMITADOR_JANELA", "2"))
# Endpoint NATIVO do Ollama via OpenWebUI. O /api/chat/completions (OpenAI-compat)
# IGNORA options.num_ctx e capa o prompt em 4096 tokens; o /ollama/api/chat respeita.
DELIMITADOR_ENDPOINT = os.environ.get("DELIMITADOR_ENDPOINT", "/ollama/api/chat")
# Janela de contexto pedida ao modelo (so vale no endpoint nativo).
# Meio-termo: 8192 cabe ~2500 chars/pagina x 5 paginas com folga e e rapido.
# O experimento da Busca #36 mostrou que 16384/6000 nao melhorou e ficou 2,5x
# mais lento (~40s/doc), entao ficamos no equilibrio.
DELIMITADOR_NUM_CTX = int(os.environ.get("DELIMITADOR_NUM_CTX", "8192"))
# Quantos caracteres de cada pagina enviar ao delimitador (antes: 1100 fixo).
DELIMITADOR_TRECHO = int(os.environ.get("DELIMITADOR_TRECHO", "2500"))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "apps": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
