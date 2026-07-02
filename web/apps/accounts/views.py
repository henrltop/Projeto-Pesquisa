from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.core.providers import ProviderError, listar_modelos

from .forms import DeveloperForm
from .models import MODELO_OPENAI_PADRAO, UserProfile


@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = DeveloperForm(request.POST)
        if form.is_valid():
            profile_obj.provider = form.cleaned_data["provider"]
            profile_obj.openwebui_base_url = form.cleaned_data.get("openwebui_base_url") or ""
            nova_chave = form.cleaned_data.get("api_key") or ""
            if nova_chave:
                profile_obj.set_openai_key(nova_chave)
            modelo = form.cleaned_data.get("modelo_selecionado") or ""
            if profile_obj.provider == UserProfile.Provider.OPENAI:
                profile_obj.modelo_selecionado = MODELO_OPENAI_PADRAO
            else:
                profile_obj.modelo_selecionado = modelo
            profile_obj.ver_respostas_brutas = form.cleaned_data.get("ver_respostas_brutas", False)
            profile_obj.save()
            messages.success(request, "Configuracoes de desenvolvedor atualizadas.")
            return redirect("accounts:profile")
    else:
        form = DeveloperForm(initial={
            "provider": profile_obj.provider,
            "openwebui_base_url": profile_obj.openwebui_base_url,
            "modelo_selecionado": profile_obj.modelo_selecionado,
            "ver_respostas_brutas": profile_obj.ver_respostas_brutas,
        })

    return render(
        request,
        "accounts/profile.html",
        {
            "form": form,
            "profile": profile_obj,
            "modelo_openai_padrao": MODELO_OPENAI_PADRAO,
        },
    )


@login_required
@require_POST
def validar_provedor(request):
    """Endpoint HTMX: recebe provider + api_key + base_url, devolve fragmento com modelos."""
    provider = request.POST.get("provider") or ""
    base_url = request.POST.get("openwebui_base_url") or ""
    api_key = (request.POST.get("api_key") or "").strip()

    if provider not in dict(UserProfile.Provider.choices):
        return HttpResponseBadRequest("provider invalido")

    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    if not api_key:
        api_key = profile_obj.get_openai_key() or ""

    contexto = {
        "provider": provider,
        "modelo_openai_padrao": MODELO_OPENAI_PADRAO,
        "modelo_atual": profile_obj.modelo_selecionado,
    }

    if provider == UserProfile.Provider.OPENAI:
        try:
            listar_modelos("openai", api_key)
        except ProviderError as exc:
            contexto["erro"] = str(exc)
        else:
            contexto["ok"] = True
        return render(request, "accounts/_modelos.html", contexto)

    try:
        modelos = listar_modelos("openwebui", api_key, base_url=base_url)
    except ProviderError as exc:
        contexto["erro"] = str(exc)
    else:
        contexto["modelos"] = modelos
    return render(request, "accounts/_modelos.html", contexto)
