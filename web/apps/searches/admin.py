from django.contrib import admin

from .models import SearchJob


@admin.register(SearchJob)
class SearchJobAdmin(admin.ModelAdmin):
    list_display = (
        "id", "termo", "ano_inicio", "ano_fim", "status",
        "total_extraidos", "total_relevantes", "total_duvidosos", "criado_por", "created_at",
    )
    list_filter = ("status", "busca_exata", "criado_por")
    search_fields = ("termo",)
    readonly_fields = (
        "celery_task_id", "created_at", "started_at", "finished_at",
        "total_extraidos", "total_relevantes", "total_duvidosos",
        "total_descartados", "total_erros", "total_reaproveitados",
        "custo_estimado_usd", "mensagem_erro",
    )
