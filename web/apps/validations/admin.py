from django.contrib import admin

from .models import BlindItem, BlindSession


class BlindItemInline(admin.TabularInline):
    model = BlindItem
    extra = 0
    readonly_fields = (
        "document", "ordem", "categoria_ia", "decisao_humana",
        "resultado_binario", "concordancia", "fonte", "reviewed_at",
    )
    fields = readonly_fields


@admin.register(BlindSession)
class BlindSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "tamanho_amostra", "status", "aproveitou_avaliados", "created_at")
    list_filter = ("status",)
    readonly_fields = ("created_at", "finished_at")
    inlines = [BlindItemInline]


@admin.register(BlindItem)
class BlindItemAdmin(admin.ModelAdmin):
    list_display = (
        "id", "session", "document", "ordem", "categoria_ia",
        "decisao_humana", "concordancia", "fonte",
    )
    list_filter = ("categoria_ia", "concordancia", "fonte")
    readonly_fields = ("created_at", "reviewed_at")
