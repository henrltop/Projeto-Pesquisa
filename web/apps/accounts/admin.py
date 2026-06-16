from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "modelo_selecionado", "ver_respostas_brutas",
                    "has_openai_key", "updated_at")
    list_editable = ("ver_respostas_brutas",)
    list_filter = ("provider", "ver_respostas_brutas")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("openai_key_ciphertext", "created_at", "updated_at")
