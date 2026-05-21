from django.conf import settings
from django.db import models


class Review(models.Model):
    class Decisao(models.TextChoices):
        SUPER_RELEVANTE = "super_relevante", "Super relevante"
        APROVADO = "aprovado", "Aprovado"
        RESSALVA = "ressalva", "Aprovado com ressalva"
        REJEITADO = "rejeitado", "Rejeitado"

    document = models.ForeignKey(
        "documents.Document", on_delete=models.CASCADE, related_name="reviews",
    )
    revisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="revisoes",
    )
    decisao = models.CharField(max_length=20, choices=Decisao.choices, db_index=True)
    comentario = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        # Um documento tem no maximo uma revisao final; alterar = sobrescrever.
        constraints = [
            models.UniqueConstraint(fields=["document"], name="uniq_review_por_documento"),
        ]
        verbose_name = "Revisao"
        verbose_name_plural = "Revisoes"

    def __str__(self) -> str:
        return f"{self.document} -> {self.get_decisao_display()} (por {self.revisor})"
