#!/usr/bin/env bash

# Instalar dependências (caso queira manter no start)
pip install -r requirements.txt

# Coletar estáticos
python manage.py collectstatic --noinput --settings=arqia.settings.prod

# Aplicar migrações
#python manage.py makemigrations --settings=arqia.settings.prod

#python manage.py migrate --settings=arqia.settings.prod

# Criar superusuário apenas se não existir
echo "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@email.com', 'admin1234')
" | python manage.py shell --settings=arqia.settings.prod

# Iniciar o servidor
gunicorn arqia.wsgi:application --bind 0.0.0.0:8000

apt-get update && apt-get install -y poppler-utils