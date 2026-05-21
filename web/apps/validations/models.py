from django.conf import settings
from django.db import models
from django.utils import timezone


class BlindSession(models.Model):
    class Status(models.TextChoices):
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        CONCLUIDA = "concluida", "Concluida"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blind_sessions",
    )
    tamanho_amostra = models.PositiveIntegerField()
    aproveitou_avaliados = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.EM_ANDAMENTO,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Sessao #{self.pk} ({self.tamanho_amostra} docs, {self.status})"

    @property
    def total_avaliados(self) -> int:
        return self.items.filter(decisao_humana__isnull=False).exclude(decisao_humana="").count()

    @property
    def progresso_pct(self) -> int:
        total = self.items.count()
        if total == 0:
            return 0
        return min(100, round(100 * self.total_avaliados / total))

    @property
    def proximo_item(self):
        return (
            self.items
            .filter(models.Q(decisao_humana__isnull=True) | models.Q(decisao_humana=""))
            .order_by("ordem")
            .first()
        )

    def verificar_conclusao(self):
        if self.proximo_item is None and self.status != self.Status.CONCLUIDA:
            self.status = self.Status.CONCLUIDA
            self.finished_at = timezone.now()
            self.save(update_fields=["status", "finished_at"])


class BlindItem(models.Model):
    class Decisao(models.TextChoices):
        SUPER_RELEVANTE = "super_relevante", "Super relevante"
        APROVADO = "aprovado", "Aprovado"
        RESSALVA = "ressalva", "Aprovado com ressalva"
        REJEITADO = "rejeitado", "Rejeitado"

    class Fonte(models.TextChoices):
        SORTEADO = "sorteado", "Sorteado"
        REAPROVEITADO = "reaproveitado", "Reaproveitado"

    session = models.ForeignKey(
        BlindSession, on_delete=models.CASCADE, related_name="items",
    )
    document = models.ForeignKey(
        "documents.Document", on_delete=models.CASCADE, related_name="blind_items",
    )
    ordem = models.PositiveIntegerField()

    categoria_ia = models.CharField(max_length=20, db_index=True)
    tipo_ato_ia = models.CharField(max_length=120, blank=True)
    justificativa_ia = models.TextField(blank=True)

    decisao_humana = models.CharField(
        max_length=20, choices=Decisao.choices, blank=True, null=True,
    )
    observacao = models.TextField(blank=True)

    resultado_binario = models.CharField(max_length=16, blank=True)
    concordancia = models.BooleanField(null=True)

    tempo_avaliacao_segundos = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    fonte = models.CharField(
        max_length=16, choices=Fonte.choices, default=Fonte.SORTEADO,
    )

    class Meta:
        ordering = ("ordem",)
        constraints = [
            models.UniqueConstraint(
                fields=["session", "document"],
                name="uniq_blind_item_por_sessao",
            ),
        ]

    def __str__(self):
        return f"Item #{self.ordem} sessao={self.session_id} doc={self.document_id}"

    @staticmethod
    def _binario_humano(decisao: str) -> str:
        if decisao in ("super_relevante", "aprovado", "ressalva"):
            return "relevante"
        return "nao_relevante"

    @staticmethod
    def _binario_ia(categoria: str) -> str:
        if categoria in ("super_relevante", "relevante"):
            return "relevante"
        return "nao_relevante"

    def save(self, **kwargs):
        if self.decisao_humana:
            self.resultado_binario = self._binario_humano(self.decisao_humana)
            self.concordancia = (
                self.resultado_binario == self._binario_ia(self.categoria_ia)
            )
        super().save(**kwargs)
