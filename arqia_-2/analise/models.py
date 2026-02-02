import os
from django.db import models
from django.contrib.auth.models import User

def upload_to(instance, filename):
    """Define o caminho para upload de arquivos"""
    return os.path.join('uploads', filename)

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome or f"Categoria #{self.id}"

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'


class Documento(models.Model):
    class Status(models.TextChoices):
        QUEUED = 'queued', 'Na fila'
        PROCESSING = 'processing', 'Processando'
        DONE = 'done', 'Concluido'
        ERROR = 'error', 'Erro'

    CATEGORIAS = [
        ('alimentos', 'Alimentos'),
        ('medicamentos', 'Medicamentos'),
        ('cosmeticos', 'Cosméticos'),
        ('veterinario', 'Veterinário'),
        ('saneantes', 'Saneantes'),
        ('tabaco', 'Tabaco'),
        ('estetica', 'Estética'),
        ('outros', 'Outros'),
    ]

    nome_arquivo = models.CharField(max_length=255)
    arquivo = models.FileField(upload_to=upload_to, null=True, blank=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos'
    )
    texto_extraido = models.TextField(blank=True, null=True)
    resultado_analise = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.QUEUED,
        db_index=True,
    )
    error_message = models.CharField(max_length=255, blank=True, default='')
    data_envio = models.DateTimeField(auto_now_add=True)

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos'
    )

    def __str__(self):
        return self.nome_arquivo or f"Documento #{self.id}"

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-data_envio']


class LogDeSistema(models.Model):
    acao = models.CharField(max_length=100)
    mensagem = models.TextField()

    documento = models.ForeignKey(
        Documento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs'
    )
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        doc = f" - Doc #{self.documento.id}" if self.documento else ""
        return f"[{self.data.strftime('%d/%m %H:%M')}] {self.acao.upper()}{doc}"

    class Meta:
        verbose_name = 'Log de Sistema'
        verbose_name_plural = 'Logs de Sistema'
