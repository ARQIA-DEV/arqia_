from arqia.settings.base import *
from decouple import config
import dj_database_url

DEBUG = True
SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(",")  # suporta múltiplos

DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL"), 
        conn_max_age=600
    )
}
