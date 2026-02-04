from django.test import TestCase
from django.contrib.auth.models import User

from .models import Categoria, Documento
from .serializers import DocumentoSerializer


class DocumentoSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="teste", password="senha123")

    def test_retorna_categoria_nome_e_status_label(self):
        categoria = Categoria.objects.create(nome="medicamentos")
        documento = Documento.objects.create(
            nome_arquivo="laudo.pdf",
            categoria=categoria,
            status=Documento.Status.QUEUED,
            usuario=self.user,
        )

        data = DocumentoSerializer(documento).data

        self.assertEqual(data["categoria_nome"], "medicamentos")
        self.assertEqual(data["status_label"], "Na fila")

    def test_retorna_categoria_nome_none_quando_documento_sem_categoria(self):
        documento = Documento.objects.create(
            nome_arquivo="laudo-sem-categoria.pdf",
            status=Documento.Status.ERROR,
            usuario=self.user,
        )

        data = DocumentoSerializer(documento).data

        self.assertIsNone(data["categoria_nome"])
        self.assertEqual(data["status_label"], "Erro")
