import os
from django.contrib import admin, messages
from .models import Documento, Categoria
from .utils import analisar_documento_por_tipo

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('nome_arquivo', 'categoria', 'status', 'data_envio')
    search_fields = ('nome_arquivo',)
    list_filter = ('categoria', 'status', 'data_envio')
    actions = ['reanalisar_documentos']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        try:
            if obj.arquivo and hasattr(obj.arquivo, 'path'):
                tipo = os.path.splitext(obj.arquivo.name)[1].lower().replace('.', '')
                if tipo in ['pdf', 'docx', 'xlsx', 'dwg', 'ifc']:
                    resultado = analisar_documento_por_tipo(obj.arquivo.path, tipo)
                    obj.resultado_analise = resultado
                    obj.status = Documento.Status.DONE
                    obj.error_message = ''
                    obj.save()
                    self.message_user(request, "Análise realizada com sucesso ✅", messages.SUCCESS)
        except Exception as e:
            obj.status = Documento.Status.ERROR
            obj.error_message = str(e)[:255]
            obj.save()
            self.message_user(request, f"Erro ao analisar: {e}", level=messages.ERROR)

    @admin.action(description='🔁 Reanalisar documentos selecionados')
    def reanalisar_documentos(self, request, queryset):
        for doc in queryset:
            try:
                tipo = os.path.splitext(doc.arquivo.name)[1].lower().replace('.', '')
                if tipo in ['pdf', 'docx', 'xlsx', 'dwg', 'ifc']:
                    resultado = analisar_documento_por_tipo(doc.arquivo.path, tipo)
                    doc.resultado_analise = resultado
                    doc.status = Documento.Status.DONE
                    doc.error_message = ''
                    doc.save()
            except Exception as e:
                doc.status = Documento.Status.ERROR
                doc.error_message = str(e)[:255]
                doc.save()
                self.message_user(request, f"Erro ao reanalisar {doc}: {e}", level=messages.ERROR)
        self.message_user(request, f"{queryset.count()} documentos reanalisados com sucesso ✅", messages.SUCCESS)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

admin.site.site_header = "Administração do Sistema"
admin.site.site_title = "Administração Django"
admin.site.index_title = "Gerenciamento de Arquivos"
