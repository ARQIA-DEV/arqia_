from rest_framework import serializers
from .models import Documento

class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = '__all__'
        read_only_fields = ['id', 'usuario', 'data_envio', 'texto_extraido', 'resultado_analise']
