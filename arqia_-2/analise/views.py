import os
import uuid
import logging
from base64 import b64encode

from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import Documento, Categoria, LogDeSistema
from .permissions import IsAuthenticatedOrOptions
from .serializers import DocumentoSerializer
from .tasks import analisar_documento_task
from .prompts import PROMPT_MAP  # Importação do mapa de prompts

logger = logging.getLogger(__name__)

def healthcheck(request):
    return JsonResponse({"status": "ok"})

class ListaDocumentosView(ListAPIView):
    serializer_class = DocumentoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['categoria', 'status']

    def get_queryset(self):
        return Documento.objects.filter(usuario=self.request.user)

class DetalheDocumentoView(RetrieveAPIView):
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(self.queryset, pk=self.kwargs["pk"], usuario=self.request.user)

class AnaliseDocumentoView(APIView):
    permission_classes = [IsAuthenticatedOrOptions]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if 'arquivo' not in request.FILES or 'categoria' not in request.data:
            return Response({"erro": "Arquivo e categoria são obrigatórios"}, status=400)

        arquivo = request.FILES['arquivo']
        categoria_nome = request.data['categoria']
        categoria_slug = categoria_nome.strip().lower()
        nome_original = arquivo.name
        extensao = nome_original.split('.')[-1].lower()
        tipos_suportados = ['pdf']

        if not categoria_slug:
            return Response({"erro": "Categoria inválida."}, status=400)

        if arquivo.size > 5 * 1024 * 1024:
            return Response({"erro": "Arquivo muito grande. Tamanho máximo: 5MB"}, status=400)

        if extensao not in tipos_suportados:
            return Response(
                {"erro": "No momento, apenas arquivos PDF são suportados para análise automatizada."},
                status=400,
            )

        nome_unico = f"{uuid.uuid4().hex}_{nome_original}"
        caminho = os.path.join(settings.MEDIA_ROOT, 'uploads', nome_unico)
        os.makedirs(os.path.dirname(caminho), exist_ok=True)

        try:
            with open(caminho, 'wb+') as f:
                for chunk in arquivo.chunks():
                    f.write(chunk)
        except Exception:
            logger.exception("Erro ao salvar o arquivo no servidor.")
            return Response({"erro": "Erro ao salvar o arquivo."}, status=500)

        try:
            documento = Documento.objects.create(
                nome_arquivo=nome_original,
                categoria=Categoria.objects.get_or_create(nome=categoria_slug)[0],
                arquivo=f'uploads/{nome_unico}',
                status=Documento.Status.QUEUED,
                error_message='',
                usuario=request.user
            )

            with open(caminho, 'rb') as f:
                arquivo_base64 = b64encode(f.read()).decode()

            prompt = PROMPT_MAP.get(categoria_slug, PROMPT_MAP["outros"])

            analisar_documento_task.delay(
                documento.id,
                arquivo_base64,
                extensao,
                categoria_slug,
                prompt,
                request.user.id
            )
            

            LogDeSistema.objects.create(
                acao="Análise agendada",
                mensagem="Documento enviado para análise assíncrona.",
                documento=documento,
                usuario=request.user
            )

            return Response({
                "mensagem": "Documento enviado para análise. Você será notificado quando estiver pronto.",
                "documento_id": documento.id,
                "status": documento.status,
            }, status=202)

        except Exception:
            logger.exception("Erro ao processar a análise.")
            return Response({"erro": "Erro ao analisar documento."}, status=500)
