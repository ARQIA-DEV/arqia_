from rest_framework import serializers
from .models import Documento

class DocumentoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()

    class Meta:
        model = Documento
        fields = '__all__'
        read_only_fields = [
            'id',
            'usuario',
            'data_envio',
            'texto_extraido',
            'resultado_analise',
            'status',
            'error_message',
        ]

    def get_categoria_nome(self, obj):
        return obj.categoria.nome if obj.categoria else None

    def get_status_label(self, obj):
        return obj.get_status_display()
