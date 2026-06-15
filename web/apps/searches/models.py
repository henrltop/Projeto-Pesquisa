from django.conf import settings
from django.db import models
from django.urls import reverse


class SearchJob(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        EXTRAINDO = "extraindo", "Extraindo do IOMAT"
        CLASSIFICANDO = "classificando", "Classificando com IA"
        PAUSADO = "pausado", "Pausado"
        CONCLUIDO = "concluido", "Concluido"
        FALHOU = "falhou", "Falhou"
        CANCELADO = "cancelado", "Cancelado"

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="buscas",
    )

    termo = models.CharField(max_length=300)
    busca_exata = models.BooleanField(default=True)
    forcar_reclassificacao = models.BooleanField(default=False)
    usar_delimitador = models.BooleanField(default=True)
    ano_inicio = models.PositiveIntegerField()
    ano_fim = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDENTE, db_index=True,
    )
    celery_task_id = models.CharField(max_length=64, blank=True, default="")
    mensagem_erro = models.TextField(blank=True, default="")

    total_extraidos = models.PositiveIntegerField(default=0)
    total_relevantes = models.PositiveIntegerField(default=0)
    total_duvidosos = models.PositiveIntegerField(default=0)
    total_descartados = models.PositiveIntegerField(default=0)
    total_erros = models.PositiveIntegerField(default=0)
    total_reaproveitados = models.PositiveIntegerField(default=0)

    custo_estimado_usd = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    # --- Campos de progresso fino (atualizados pela task em tempo real) ---
    fase_atual = models.CharField(max_length=120, blank=True, default="")
    ano_atual = models.PositiveIntegerField(null=True, blank=True)
    doc_atual = models.PositiveIntegerField(default=0)
    mensagem_progresso = models.CharField(max_length=300, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Busca"
        verbose_name_plural = "Buscas"

    def __str__(self) -> str:
        return f"{self.termo} [{self.ano_inicio}-{self.ano_fim}] ({self.get_status_display()})"

    def get_absolute_url(self) -> str:
        return reverse("searches:detail", args=[self.pk])

    @property
    def em_andamento(self) -> bool:
        return self.status in {self.Status.PENDENTE, self.Status.EXTRAINDO, self.Status.CLASSIFICANDO}

    @property
    def pausavel(self) -> bool:
        """Pode receber o comando de pausa (esta rodando)."""
        return self.em_andamento

    @property
    def retomavel(self) -> bool:
        """Pode ser retomado de onde parou (idempotencia pula o ja feito)."""
        return self.status in {self.Status.PAUSADO, self.Status.CANCELADO, self.Status.FALHOU}

    @property
    def total_processados(self) -> int:
        return self.total_relevantes + self.total_duvidosos + self.total_descartados + self.total_erros

    @property
    def percentual(self) -> int:
        if not self.total_extraidos:
            return 0
        return min(100, int(100 * self.total_processados / self.total_extraidos))

    @property
    def duracao_segundos(self) -> int | None:
        if not self.started_at:
            return None
        fim = self.finished_at or _now()
        return max(0, int((fim - self.started_at).total_seconds()))

    @property
    def eta_segundos(self) -> int | None:
        """Estima quanto falta baseado no ritmo atual de classificacao."""
        if self.status != self.Status.CLASSIFICANDO:
            return None
        proc = self.total_processados
        if not proc or not self.total_extraidos or not self.started_at:
            return None
        restante = max(0, self.total_extraidos - proc)
        if not restante:
            return 0
        elapsed = (_now() - self.started_at).total_seconds()
        if elapsed <= 0:
            return None
        ritmo = proc / elapsed  # docs/seg
        if ritmo <= 0:
            return None
        return int(restante / ritmo)


def _now():
    from django.utils import timezone
    return timezone.now()


class PipelineStage(models.Model):
    """Uma etapa da pipeline de um SearchJob. Permite visualizar a esteira no frontend."""

    class Estado(models.TextChoices):
        QUEUED  = "queued",  "Na fila"
        RUNNING = "running", "Em execucao"
        DONE    = "done",    "Concluida"
        FAILED  = "failed",  "Falhou"
        SKIPPED = "skipped", "Pulada"

    class Agente(models.TextChoices):
        AI  = "AI",  "IA"
        HUM = "HUM", "Humano"
        SYS = "SYS", "Sistema"

    search_job = models.ForeignKey(
        SearchJob, on_delete=models.CASCADE, related_name="stages",
    )
    ordem       = models.PositiveSmallIntegerField()
    codigo      = models.CharField(max_length=40)   # extracao / dedup / classificacao / download / indexacao / revisao
    nome        = models.CharField(max_length=80)   # "Extracao IOMAT"
    detalhe     = models.CharField(max_length=160, blank=True, default="")
    agente      = models.CharField(max_length=5, choices=Agente.choices, default=Agente.SYS)
    estado      = models.CharField(max_length=10, choices=Estado.choices, default=Estado.QUEUED)
    itens_total = models.PositiveIntegerField(default=0)
    itens_feitos = models.PositiveIntegerField(default=0)
    started_at  = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    mensagem    = models.CharField(max_length=250, blank=True, default="")

    class Meta:
        ordering = ("search_job", "ordem")
        verbose_name = "Etapa da pipeline"
        verbose_name_plural = "Etapas da pipeline"
        constraints = [
            models.UniqueConstraint(fields=["search_job", "codigo"], name="uniq_stage_per_job"),
        ]

    def __str__(self) -> str:
        return f"{self.search_job_id}#{self.ordem} {self.nome} [{self.estado}]"

    @property
    def duracao_segundos(self) -> int | None:
        if not self.started_at:
            return None
        fim = self.finished_at or _now()
        return max(0, int((fim - self.started_at).total_seconds()))

    @property
    def percentual(self) -> int:
        if not self.itens_total:
            return 100 if self.estado == self.Estado.DONE else 0
        return min(100, int(100 * self.itens_feitos / self.itens_total))

    # --- Helpers usados pela task ---
    def iniciar(self, total: int | None = None, detalhe: str = "", mensagem: str = "") -> None:
        from django.utils import timezone
        self.estado = self.Estado.RUNNING
        self.started_at = timezone.now()
        if total is not None:
            self.itens_total = total
        if detalhe:
            self.detalhe = detalhe
        if mensagem:
            self.mensagem = mensagem
        self.save(update_fields=["estado", "started_at", "itens_total", "detalhe", "mensagem"])

    def tick(self, feitos: int | None = None, mensagem: str = "") -> None:
        fields = []
        if feitos is not None:
            self.itens_feitos = feitos
            fields.append("itens_feitos")
        if mensagem:
            self.mensagem = mensagem[:250]
            fields.append("mensagem")
        if fields:
            self.save(update_fields=fields)

    def concluir(self, mensagem: str = "") -> None:
        from django.utils import timezone
        self.estado = self.Estado.DONE
        self.finished_at = timezone.now()
        if self.itens_total:
            self.itens_feitos = self.itens_total
        if mensagem:
            self.mensagem = mensagem[:250]
        self.save(update_fields=["estado", "finished_at", "itens_feitos", "mensagem"])

    def falhar(self, mensagem: str) -> None:
        from django.utils import timezone
        self.estado = self.Estado.FAILED
        self.finished_at = timezone.now()
        self.mensagem = mensagem[:250]
        self.save(update_fields=["estado", "finished_at", "mensagem"])

    def pular(self, mensagem: str = "") -> None:
        from django.utils import timezone
        self.estado = self.Estado.SKIPPED
        self.finished_at = timezone.now()
        if mensagem:
            self.mensagem = mensagem[:250]
        self.save(update_fields=["estado", "finished_at", "mensagem"])


# Definicao das 6 etapas padrao. Criadas por SearchJob.
STAGES_PADRAO = [
    {"ordem": 1, "codigo": "extracao",       "nome": "Extracao IOMAT",       "agente": PipelineStage.Agente.SYS, "detalhe": "consulta a API publica por ano"},
    {"ordem": 2, "codigo": "dedup",          "nome": "Deduplicacao",         "agente": PipelineStage.Agente.SYS, "detalhe": "elimina paginas repetidas do banco"},
    {"ordem": 3, "codigo": "classificacao",  "nome": "Classificacao IA",     "agente": PipelineStage.Agente.AI,  "detalhe": "3 niveis: relevante / duvidoso / irrelevante"},
    {"ordem": 4, "codigo": "download",       "nome": "Download de PDFs",     "agente": PipelineStage.Agente.SYS, "detalhe": "apenas relevantes e duvidosos"},
    {"ordem": 5, "codigo": "indexacao",      "nome": "Indexacao full-text",  "agente": PipelineStage.Agente.SYS, "detalhe": "Postgres SearchVector em portugues"},
    {"ordem": 6, "codigo": "revisao",        "nome": "Revisao humana",       "agente": PipelineStage.Agente.HUM, "detalhe": "aguardando avaliacao dos duvidosos"},
]


def criar_stages(job: SearchJob) -> None:
    for s in STAGES_PADRAO:
        PipelineStage.objects.get_or_create(
            search_job=job, codigo=s["codigo"],
            defaults={
                "ordem": s["ordem"], "nome": s["nome"],
                "agente": s["agente"], "detalhe": s["detalhe"],
            },
        )
