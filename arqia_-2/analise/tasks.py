import logging
from celery import shared_task
from django.contrib.auth.models import User
from .models import Documento, LogDeSistema
from .utils import analisar_pdf_com_gpt5mini_base64

logger = logging.getLogger(__name__)

@shared_task
def analisar_documento_task(documento_id, arquivo_base64, extensao, categoria_nome, prompt, user_id):
    user = None
    try:
        user = User.objects.filter(pk=user_id).first()
        documento = Documento.objects.get(pk=documento_id)
        categoria_nome = (categoria_nome or "").strip().lower()
        extensao = (extensao or "").strip().lower()
        prompt = (prompt or "").strip() or "Você é um especialista em análise de projetos."

        documento.status = Documento.Status.PROCESSING
        documento.error_message = ''
        documento.save(update_fields=["status", "error_message"])

        logger.info(
            f"[Celery] Iniciando análise do documento ID {documento_id} "
            f"({documento.nome_arquivo}) na categoria '{categoria_nome or 'outros'}'"
        )

        if extensao != "pdf":
            raise ValueError("No novo fluxo, só aceitamos PDF.")

        resultado = analisar_pdf_com_gpt5mini_base64(
            pdf_base64=arquivo_base64,
            filename=documento.nome_arquivo,
            prompt=prompt,
        )
        texto_extraido = ""

        if not resultado or resultado.strip().lower().startswith("erro"):
            raise ValueError("Falha na análise com GPT")

        documento.texto_extraido = texto_extraido
        documento.resultado_analise = resultado
        documento.status = Documento.Status.DONE
        documento.error_message = ''
        documento.save(update_fields=["texto_extraido", "resultado_analise", "status", "error_message"])

        LogDeSistema.objects.create(
            acao="Análise finalizada",
            mensagem="Análise concluída com sucesso.",
            documento=documento,
            usuario=user
        )

        logger.info(f"[Celery] ✅ Análise concluída com sucesso para o documento ID {documento_id}")
        return {"documento_id": documento_id, "status": Documento.Status.DONE}

    except Exception as e:
        logger.exception(f"[Celery] ❌ Erro ao analisar documento ID {documento_id}")
        documento = Documento.objects.filter(pk=documento_id).first()
        if documento:
            documento.status = Documento.Status.ERROR
            documento.error_message = str(e)[:255]
            documento.resultado_analise = "Erro ao processar o documento automaticamente. A equipe será notificada."
            documento.save(update_fields=["status", "error_message", "resultado_analise"])
            LogDeSistema.objects.create(
                acao="Erro na análise",
                mensagem=str(e)[:500],
                documento=documento,
                usuario=user if user else None
            )
        raise
