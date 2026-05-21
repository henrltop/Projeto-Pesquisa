from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "decisao", "revisor", "created_at")
    list_filter = ("decisao", "revisor")
    search_fields = ("comentario",)
    readonly_fields = ("created_at",)
