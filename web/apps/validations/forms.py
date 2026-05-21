from django import forms

from .models import BlindItem


class SessionConfigForm(forms.Form):
    tamanho_amostra = forms.IntegerField(
        min_value=30,
        max_value=300,
        initial=150,
        label="Tamanho da amostra",
        help_text="Multiplo de 3. Sera dividido igualmente entre relevantes, duvidosos e irrelevantes.",
        widget=forms.NumberInput(attrs={
            "class": "t-input",
            "step": "3",
            "style": "max-width:160px;",
        }),
    )
    aproveitou_avaliados = forms.BooleanField(
        required=False,
        label="Aproveitar avaliacoes anteriores",
        help_text=(
            "Reutiliza revisoes que voce ja fez. "
            "Atencao: marcar esta opcao pode introduzir vies nos resultados, "
            "pois as avaliacoes anteriores nao foram feitas em condicoes cegas."
        ),
    )

    def clean_tamanho_amostra(self):
        val = self.cleaned_data["tamanho_amostra"]
        return val - (val % 3)


class BlindReviewForm(forms.ModelForm):
    class Meta:
        model = BlindItem
        fields = ("decisao_humana", "observacao")
        widgets = {
            "decisao_humana": forms.RadioSelect,
            "observacao": forms.Textarea(attrs={
                "class": "t-input",
                "rows": 3,
                "placeholder": "Descreva o motivo da sua decisao (obrigatorio, min. 10 caracteres).",
                "required": True,
            }),
        }

    def clean_observacao(self):
        val = (self.cleaned_data.get("observacao") or "").strip()
        if len(val) < 10:
            raise forms.ValidationError("A observacao deve ter pelo menos 10 caracteres.")
        return val

    def clean_decisao_humana(self):
        val = self.cleaned_data.get("decisao_humana")
        if not val:
            raise forms.ValidationError("Selecione uma opcao.")
        return val
