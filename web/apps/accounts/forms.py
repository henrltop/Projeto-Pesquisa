from django import forms

from .models import UserProfile


class DeveloperForm(forms.Form):
    provider = forms.ChoiceField(
        label="Provedor",
        choices=UserProfile.Provider.choices,
        widget=forms.RadioSelect,
    )
    openwebui_base_url = forms.URLField(
        label="URL base do OpenWebUI",
        required=False,
        widget=forms.URLInput(attrs={
            "placeholder": "https://openwebui.exemplo.com",
            "class": "form-input",
        }),
        help_text="Somente para OpenWebUI. Ex.: https://seu-servidor/ (sem /api no final).",
    )
    api_key = forms.CharField(
        label="Chave de API",
        required=False,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Cole aqui a chave (deixe em branco para manter a atual)",
            "autocomplete": "off",
            "class": "form-input",
        }),
    )
    modelo_selecionado = forms.CharField(
        label="Modelo",
        required=False,
        widget=forms.HiddenInput(),
    )
    ver_respostas_brutas = forms.BooleanField(
        label="Ver respostas brutas da IA",
        required=False,
        help_text="Mostra o JSON cru que o modelo devolveu (para conferir veracidade). "
                  "As respostas brutas sao sempre salvas; isto so muda a exibicao.",
    )

    def clean(self):
        cleaned = super().clean()
        provider = cleaned.get("provider")
        if provider == UserProfile.Provider.OPENWEBUI and not cleaned.get("openwebui_base_url"):
            self.add_error("openwebui_base_url", "Obrigatorio para OpenWebUI.")
        return cleaned
