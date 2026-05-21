from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "has_openai_key", "created_at", "updated_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("openai_key_ciphertext", "created_at", "updated_at")
