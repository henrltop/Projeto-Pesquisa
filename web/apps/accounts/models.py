from django.conf import settings
from django.db import models

from . import crypto

MODELO_OPENAI_PADRAO = "gpt-5.4-mini"


class UserProfile(models.Model):
    class Provider(models.TextChoices):
        OPENAI = "openai", "OpenAI"
        OPENWEBUI = "openwebui", "OpenWebUI"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    openai_key_ciphertext = models.TextField(blank=True, default="")
    provider = models.CharField(
        max_length=20, choices=Provider.choices, default=Provider.OPENAI
    )
    openwebui_base_url = models.URLField(blank=True, default="")
    modelo_selecionado = models.CharField(max_length=120, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

    def __str__(self) -> str:
        return f"Perfil de {self.user}"

    def set_openai_key(self, plaintext: str) -> None:
        self.openai_key_ciphertext = crypto.encrypt(plaintext) if plaintext else ""

    def get_openai_key(self) -> str | None:
        return crypto.decrypt(self.openai_key_ciphertext) if self.openai_key_ciphertext else None

    @property
    def has_openai_key(self) -> bool:
        return bool(self.openai_key_ciphertext)

    @property
    def openai_key_masked(self) -> str:
        key = self.get_openai_key()
        return crypto.mask(key) if key else ""

    @property
    def modelo_efetivo(self) -> str:
        if self.provider == self.Provider.OPENAI:
            return MODELO_OPENAI_PADRAO
        return self.modelo_selecionado or ""

    @property
    def base_url_efetivo(self) -> str | None:
        """Base URL a passar ao SDK da OpenAI. None para OpenAI oficial."""
        if self.provider == self.Provider.OPENWEBUI and self.openwebui_base_url:
            return self.openwebui_base_url.rstrip("/") + "/api"
        return None
