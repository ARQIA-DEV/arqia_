
#import os
#from pathlib import Path
#from datetime import timedelta
#from dotenv import load_dotenv
#import dj_database_url

# 🔹 Carregar variáveis de ambiente
#load_dotenv()

# 🔹 Caminho base do projeto
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 🔐 Melhor Segurança
#SECRET_KEY = os.getenv("SECRET_KEY", "chave-secreta-padrao")

#DEBUG = False  # 🔹 Segurança: Nunca usar DEBUG=True em produção!

#ALLOWED_HOSTS = ['.onrender.com', 'localhost', '127.0.0.1']  # 🔹 Especifique domínios confiáveis

# 🔹 Configuração do Banco de Dados (Segurança melhorada)
#DATABASES = {
#    'default': dj_database_url.config(conn_max_age=600)
#}
#
#TEMPLATES = [
#    {
#        'BACKEND': 'django.template.backends.django.DjangoTemplates',
#        'DIRS': [],
#        'APP_DIRS': True,
#        'OPTIONS': {
#            'context_processors': [
#                'django.template.context_processors.debug',
#                'django.template.context_processors.request',
#                'django.contrib.auth.context_processors.auth',
#                'django.contrib.messages.context_processors.messages',
#            ],
#        },
#    },
#]

# Configuração de arquivos estáticos
#STATIC_URL = '/static/'
#STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 🔹 Configuração do Token JWT para autenticação
#INSTALLED_APPS = [
#    'django.contrib.admin',
#    'django.contrib.auth',
#    'django.contrib.contenttypes',
#    'django.contrib.sessions',
#    'django.contrib.messages',
#    'django.contrib.staticfiles',
#    'rest_framework',
#    'rest_framework_simplejwt',  # 🔹 Adicionado para autenticação JWT
#    'analise',
#    'corsheaders',
#    'django_filters', # 🔹 Proteção CORS
#]

#MIDDLEWARE = [
#    'django.middleware.security.SecurityMiddleware',
#    'whitenoise.middleware.WhiteNoiseMiddleware',
#    'django.contrib.sessions.middleware.SessionMiddleware',
#    'corsheaders.middleware.CorsMiddleware',  # 🔹 Proteção contra acessos não autorizados
#    'django.middleware.common.CommonMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.messages.middleware.MessageMiddleware',
#    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#    
#]
#
# 🔹 Definição de permissão padrão
#REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
  #      'rest_framework_simplejwt.authentication.JWTAuthentication',
  #  ),
  #  'DEFAULT_PERMISSION_CLASSES': [
  #      'rest_framework.permissions.IsAuthenticated',  # 🔐 Agora só usuários autenticados acessam a API
  #  ],
  #  'DEFAULT_FILTER_BACKENDS': [
  #      'django_filters.rest_framework.DjangoFilterBackend'],
#}

# 🔹 Configuração dos Tokens JWT (Tokens curtos e seguros)
#SIMPLE_JWT = {
#    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
#    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
#    'ROTATE_REFRESH_TOKENS': True,
#    'BLACKLIST_AFTER_ROTATION': True,
#}

# 🔹 Proteção CORS (Apenas acessos confiáveis permitidos)
#CORS_ALLOWED_ORIGINS = [
#    "http://localhost:3000",  # 🔹 Frontend
#    "http://127.0.0.1:3000"
#]

#MEDIA_URL = '/media/'
#MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
#os.makedirs(MEDIA_ROOT, exist_ok=True)

#ROOT_URLCONF = 'arqia.urls'
#
#DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'