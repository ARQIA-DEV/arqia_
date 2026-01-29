from django.contrib import admin
from django.urls import path, include
from analise.views import healthcheck

urlpatterns = [
    path('', healthcheck, name='root-healthcheck'),
    path('admin/', admin.site.urls),         # Acesso ao admin
    path('api/', include('analise.urls')),   # Todas as rotas da app analise
]
