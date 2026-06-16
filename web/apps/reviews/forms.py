from django import forms

from apps.documents.models import Classification

from .models import Review


class ReviewForm(forms.ModelForm):
    # Qual decisao humana "concorda" com cada classificacao da IA. Se o revisor
    # escolher decisao diferente desta, ele esta DISCORDANDO e precisa justificar.
    # (Duvidoso nao entra: e uma resolucao, nao um concordar/discordar.)
    CONCORDA_COM_IA = {
        Classification.Classificacao.SUPER_RELEVANTE: Review.Decisao.SUPER_RELEVANTE,
        Classification.Classificacao.RELEVANTE: Review.Decisao.APROVADO,
        Classification.Classificacao.IRRELEVANTE: Review.Decisao.REJEITADO,
    }

    def __init__(self, *args, classificacao_ia=None, **kwargs):
        self.classificacao_ia = classificacao_ia
        super().__init__(*args, **kwargs)

    class Meta:
        model = Review
        fields = ("decisao", "comentario")
        widgets = {
            "decisao": forms.RadioSelect(),
            "comentario": forms.Textarea(attrs={
                "rows": 3, "class": "form-input",
                "placeholder": "Obrigatorio apenas se discordar da IA",
            }),
        }

    def decisao_concordante(self):
        """Decisao que representa 'concordo com a IA', ou None se nao se aplica."""
        return self.CONCORDA_COM_IA.get(self.classificacao_ia)

    def clean(self):
        cleaned = super().clean()
        decisao = cleaned.get("decisao")
        comentario = (cleaned.get("comentario") or "").strip()
        concordante = self.decisao_concordante()
        # So exige justificativa quando ha uma classificacao da IA para concordar/discordar
        # E o revisor escolheu algo diferente do "concordo".
        if concordante is not None and decisao and decisao != concordante and not comentario:
            self.add_error(
                "comentario",
                "Justifique ao discordar da classificacao da IA.",
            )
        return cleaned


def panel_context(doc, *, form=None):
    """Contexto do painel de validacao inline (usado no detalhe e na resposta HTMX)."""
    classificacoes = list(doc.classificacoes.all().order_by("-created_at"))
    classificacao_atual = classificacoes[0] if classificacoes else None
    ia_class = classificacao_atual.classificacao if classificacao_atual else None
    existente = doc.reviews.order_by("-created_at").first()
    if form is None:
        form = ReviewForm(instance=existente, classificacao_ia=ia_class)
    concordante = form.decisao_concordante()
    if form.is_bound:
        selected = form.data.get("decisao") or ""
    else:
        selected = (existente.decisao if existente else concordante) or ""
    return {
        "doc": doc,
        "existente": existente,
        "form": form,
        "classificacao_atual": classificacao_atual,
        "decisoes": Review.Decisao.choices,
        "decisao_concordante": concordante,
        "selected_decisao": selected,
    }
