from django.urls import path
from .views import (
    AnaliseDocumentoView,
    ListaDocumentosView,
    DetalheDocumentoView,
    healthcheck
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('analisar/', AnaliseDocumentoView.as_view(), name='analisar'),
    path('documentos/', ListaDocumentosView.as_view(), name='listar_documentos'),
    path('documentos/<int:pk>/', DetalheDocumentoView.as_view(), name='detalhe-documento'),
    path('health/', healthcheck, name='healthcheck'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
