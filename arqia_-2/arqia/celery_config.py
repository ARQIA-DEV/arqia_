import os
from celery import Celery  # ✅ IMPORTAR DA BIBLIOTECA CELERY, não do módulo do projeto!

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arqia.settings.prod')

app = Celery('arqia')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
