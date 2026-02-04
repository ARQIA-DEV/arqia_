from arqia.settings.base import *
from decouple import config
import dj_database_url
import re
from urllib.parse import urlparse, urlunparse
from corsheaders.defaults import default_headers
import ssl  # necessário para configurar o Redis seguro com Celery
import certifi

DEBUG = False
SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(",")

# Segurança
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Banco de Dados
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL"),
        conn_max_age=600
    )
}

# CORS
def env_csv(name: str, default: str = "") -> list[str]:
    raw = config(name, default=default)
    items = [x.strip() for x in raw.split(",") if x.strip()]
    # Remove trailing slash (evita corsheaders.E014).
    return [re.sub(r"/+$", "", x) for x in items]


CORS_ALLOWED_ORIGINS = env_csv("CORS_ALLOWED_ORIGINS", default="")

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://arqia-front-main-3(-[a-z0-9-]+)?\.vercel\.app$",
    r"^https://arqia-front-main-3(-[a-z0-9-]+)?-arqias-projects\.vercel\.app$",
]

CORS_URLS_REGEX = r"^/api/.*$"

CORS_ALLOW_CREDENTIALS = config("CORS_ALLOW_CREDENTIALS", default=False, cast=bool)
CORS_ALLOW_HEADERS = list(default_headers) + ["authorization"]


def normalize_redis_url(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    if not parsed.scheme:
        return raw_url

    # Render/Redis Cloud pode fornecer URL sem DB explícito (ex.: ...:6379/).
    if not parsed.path or parsed.path.strip("/") == "":
        parsed = parsed._replace(path="/0")
    return urlunparse(parsed)

# Static e Media
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_KEEP_ONLY_HASHED_FILES = True

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

CELERY_BROKER_URL = normalize_redis_url(config("REDIS_URL"))
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 20

if urlparse(CELERY_BROKER_URL).scheme == "rediss":
    CELERY_BROKER_USE_SSL = {
        "ssl_cert_reqs": ssl.CERT_REQUIRED,
        "ssl_ca_certs": certifi.where(),
    }
    CELERY_REDIS_BACKEND_USE_SSL = CELERY_BROKER_USE_SSL
