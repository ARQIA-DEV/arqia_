import os
import uuid
import logging
from base64 import b64encode

from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django_filters.rest_framework import DjangoFilterBackend

from openai import OpenAI
from .models import Documento, Categoria, LogDeSistema
from .serializers import DocumentoSerializer
from .tasks import analisar_documento_task
from .prompts import PROMPT_MAP  # Importação do mapa de prompts

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def healthcheck(request):
    return JsonResponse({"status": "ok"})

class ListaDocumentosView(ListAPIView):
    serializer_class = DocumentoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['categoria']

    def get_queryset(self):
        return Documento.objects.filter(usuario=self.request.user)

class DetalheDocumentoView(RetrieveAPIView):
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(self.queryset, pk=self.kwargs["pk"], usuario=self.request.user)

class AnaliseDocumentoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if 'arquivo' not in request.FILES or 'categoria' not in request.data:
            return Response({"erro": "Arquivo e categoria são obrigatórios"}, status=400)

        arquivo = request.FILES['arquivo']
        categoria_nome = request.data['categoria']
        nome_original = arquivo.name
        extensao = nome_original.split('.')[-1].lower()
        tipos_suportados = ['pdf', 'docx', 'xlsx', 'dwg', 'ifc']

        if arquivo.size > 5 * 1024 * 1024:
            return Response({"erro": "Arquivo muito grande. Tamanho máximo: 5MB"}, status=400)

        if extensao not in tipos_suportados:
            return Response({"erro": f"Tipo de arquivo não suportado: .{extensao}"}, status=400)

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
                categoria=Categoria.objects.get_or_create(nome=categoria_nome)[0],
                arquivo=f'uploads/{nome_unico}',
                usuario=request.user
            )

            with open(caminho, 'rb') as f:
                arquivo_base64 = b64encode(f.read()).decode()

            prompt = PROMPT_MAP.get(categoria_nome.lower(), PROMPT_MAP["outros"])

            analisar_documento_task.delay(
                documento.id,
                arquivo_base64,         # ou conteudo_base64
                extensao,
                categoria_nome,         # <- ESSE é o 6º argumento!
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
                "documento_id": documento.id
            }, status=202)

        except Exception:
            logger.exception("Erro ao processar a análise.")
            return Response({"erro": "Erro ao analisar documento."}, status=500)
