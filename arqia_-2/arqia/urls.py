from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),         # Acesso ao admin
    path('api/', include('analise.urls')),   # Todas as rotas da app analise
]
