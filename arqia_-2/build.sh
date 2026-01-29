#!/usr/bin/env bash

# Fail on error
set -o errexit

# Instalar dependências
pip install -r requirements.txt

# Coletar arquivos estáticos
python manage.py collectstatic --noinput --settings=arqia.settings.prod
#python manage.py migrate --settings=arqia.settings.prod
#python manage.py createsuperuser --settings=arqia.settings.prod --noinput