from django.contrib import admin

from .models import Classification, Document


class ClassificationInline(admin.TabularInline):
    model = Classification
    extra = 0
    fields = ("classificacao", "tipo_ato", "justificativa", "modelo_ia", "termo_buscado", "created_at")
    readonly_fields = fields
    can_delete = False
    show_change_link = True


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "ano", "edicao_id", "pagina", "nome_edicao", "primeiro_visto_em")
    list_filter = ("ano", "tipo_edicao")
    search_fields = ("edicao_id", "nome_edicao", "texto_bruto")
    inlines = [ClassificationInline]
    readonly_fields = ("primeiro_visto_em", "ultima_atualizacao")


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "classificacao", "tipo_ato", "termo_buscado", "created_at")
    list_filter = ("classificacao", "modelo_ia")
    search_fields = ("tipo_ato", "justificativa", "termo_buscado")
    readonly_fields = ("prompt_enviado", "resposta_crua", "created_at")
