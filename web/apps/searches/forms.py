import datetime

from django import forms

from .models import SearchJob


class SearchJobForm(forms.ModelForm):
    class Meta:
        model = SearchJob
        fields = ("termo", "busca_exata", "ano_inicio", "ano_fim")
        widgets = {
            "termo": forms.TextInput(attrs={
                "placeholder": "ex: ensino superior tecnologico",
                "class": "form-input",
                "autofocus": "autofocus",
            }),
            "ano_inicio": forms.NumberInput(attrs={"min": 1961, "max": 2030, "class": "form-input"}),
            "ano_fim": forms.NumberInput(attrs={"min": 1961, "max": 2030, "class": "form-input"}),
        }

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get("ano_inicio")
        fim = cleaned.get("ano_fim")
        if inicio and fim and inicio > fim:
            self.add_error("ano_fim", "Ano final precisa ser >= ano inicial.")
        if fim and fim > datetime.date.today().year + 1:
            self.add_error("ano_fim", "Ano final parece invalido.")
        return cleaned
