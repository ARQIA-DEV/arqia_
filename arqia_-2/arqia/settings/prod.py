from arqia.settings.base import *
from decouple import config
import dj_database_url
from corsheaders.defaults import default_headers, default_methods
import ssl  # necessário para configurar o Redis seguro com Celery
import certifi

DEBUG = False
SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(",")

# Segurança
SECURE_SSL_REDIRECT = True
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
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS").split(",")
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    "X-Requested-With",
    "X-CSRFToken",
    "Authorization",
    "Content-Type",
    "Accept"
]
CORS_ALLOW_METHODS = list(default_methods) + [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS"
]

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

CELERY_BROKER_URL = config("REDIS_URL")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

#CELERY_BROKER_USE_SSL = {
#    "ssl_cert_reqs": ssl.CERT_REQUIRED,
#    "ssl_ca_certs": certifi.where()
#}
#CELERY_REDIS_BACKEND_USE_SSL = CELERY_BROKER_USE_SSL