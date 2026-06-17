from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.urls import reverse


class Document(models.Model):
    """Pagina unica do Diario Oficial. Identidade = (edicao_id, pagina)."""

    edicao_id = models.CharField(max_length=64, db_index=True)
    tipo_edicao = models.PositiveSmallIntegerField(default=1)
    pagina = models.PositiveIntegerField()
    ano = models.PositiveIntegerField(db_index=True)

    nome_edicao = models.CharField(max_length=200, blank=True, default="")
    data_pub = models.CharField(max_length=32, blank=True, default="")
    link_oficial = models.URLField(max_length=600, blank=True, default="")

    texto_bruto = models.TextField(blank=True, default="")
    caminho_pdf = models.CharField(max_length=500, blank=True, default="")

    primeiro_visto_em = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    # Indice full-text (apenas populado em Postgres; em SQLite fica None).
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        unique_together = (("edicao_id", "pagina"),)
        indexes = [
            models.Index(fields=["ano"]),
            models.Index(fields=["edicao_id"]),
        ]
        ordering = ("-primeiro_visto_em",)

    def __str__(self) -> str:
        return f"Edicao {self.edicao_id} / pag {self.pagina} ({self.ano})"

    def get_absolute_url(self) -> str:
        return reverse("documents:detail", args=[self.pk])

    @property
    def classificacao_atual(self) -> "Classification | None":
        return self.classificacoes.order_by("-created_at").first()

    @property
    def review_final(self) -> "reviews.Review | None":  # type: ignore[name-defined]
        # Evita import circular; a relacao e definida em apps.reviews.Review.document
        return self.reviews.order_by("-created_at").first() if hasattr(self, "reviews") else None

    @property
    def estado(self) -> str:
        """Estado consolidado do documento para filtros e dashboards."""
        review = self.review_final
        if review:
            if review.decisao == "super_relevante":
                return "super_relevante_manual"
            if review.decisao == "aprovado":
                return "aprovado_manual"
            if review.decisao == "ressalva":
                return "ressalva_manual"
            return "rejeitado_manual"
        classificacao = self.classificacao_atual
        if not classificacao:
            return "aguardando_ia"
        return f"{classificacao.classificacao}_ia"

    @property
    def precisa_revisao_manual(self) -> bool:
        c = self.classificacao_atual
        return bool(c and c.classificacao == Classification.Classificacao.DUVIDOSO and not self.review_final)


class Classification(models.Model):
    class Classificacao(models.TextChoices):
        SUPER_RELEVANTE = "super_relevante", "Super Relevante"
        RELEVANTE = "relevante", "Relevante"
        DUVIDOSO = "duvidoso", "Duvidoso"
        IRRELEVANTE = "irrelevante", "Irrelevante"
        # Falha de formato: o modelo nao devolveu JSON valido com o campo
        # 'classificacao'. Guardamos a resposta_crua mesmo assim, para auditar
        # no benchmark de modelos. Nao e uma decisao de relevancia.
        ERRO = "erro", "Erro (formato)"

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="classificacoes",
    )
    search_job = models.ForeignKey(
        "searches.SearchJob", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="classificacoes",
    )
    termo_buscado = models.CharField(max_length=300, blank=True, default="")

    classificacao = models.CharField(max_length=20, choices=Classificacao.choices, db_index=True)
    tipo_ato = models.CharField(max_length=120, blank=True, default="")
    justificativa = models.TextField(blank=True, default="")

    prompt_enviado = models.TextField(blank=True, default="")
    resposta_crua = models.TextField(blank=True, default="")
    modelo_ia = models.CharField(max_length=64, blank=True, default="")
    tokens_input = models.PositiveIntegerField(null=True, blank=True)
    tokens_output = models.PositiveIntegerField(null=True, blank=True)
    com_contexto = models.BooleanField(default=False, db_index=True)
    paginas_contexto = models.CharField(max_length=120, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["classificacao"])]
        verbose_name = "Classificacao IA"
        verbose_name_plural = "Classificacoes IA"

    def __str__(self) -> str:
        return f"{self.document} -> {self.get_classificacao_display()}"
