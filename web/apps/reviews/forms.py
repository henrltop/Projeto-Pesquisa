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
