"""Helpers para listar modelos em OpenAI ou OpenWebUI."""
from __future__ import annotations

import requests

try:  # OpenWebUI institucional (IFMT) tem cert SSL invalido; silencia o warning.
    import urllib3
    urllib3.disable_warnings()
except Exception:  # noqa: BLE001
    pass


class ProviderError(Exception):
    pass


def _openai_models(api_key: str) -> list[str]:
    r = requests.get(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=15,
    )
    if r.status_code == 401:
        raise ProviderError("Chave OpenAI invalida (401).")
    if not r.ok:
        raise ProviderError(f"OpenAI retornou {r.status_code}: {r.text[:200]}")
    data = r.json().get("data") or []
    return sorted({m.get("id") for m in data if m.get("id")})


def _openwebui_models(api_key: str, base_url: str) -> list[str]:
    base = base_url.rstrip("/")
    candidatos = [f"{base}/api/models", f"{base}/v1/models", f"{base}/api/v1/models"]
    ultimo_erro = ""
    for url in candidatos:
        try:
            r = requests.get(
                url,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15,
                verify=False,  # OpenWebUI institucional (IFMT) tem cert SSL invalido
            )
        except requests.RequestException as exc:
            ultimo_erro = f"{url}: {exc}"
            continue
        if r.status_code == 401:
            raise ProviderError("Chave OpenWebUI invalida (401).")
        if r.ok:
            try:
                payload = r.json()
            except ValueError:
                ultimo_erro = f"{url}: resposta nao-JSON"
                continue
            data = payload.get("data") if isinstance(payload, dict) else payload
            if not data and isinstance(payload, dict):
                data = payload.get("models") or []
            ids: list[str] = []
            for m in data or []:
                if isinstance(m, dict):
                    ids.append(m.get("id") or m.get("name") or "")
                elif isinstance(m, str):
                    ids.append(m)
            ids = [x for x in ids if x]
            if ids:
                return sorted(set(ids))
            ultimo_erro = f"{url}: lista vazia"
        else:
            ultimo_erro = f"{url}: HTTP {r.status_code}"
    raise ProviderError(f"Nao foi possivel listar modelos do OpenWebUI. Ultimo erro: {ultimo_erro}")


def listar_modelos(provider: str, api_key: str, base_url: str = "") -> list[str]:
    if not api_key:
        raise ProviderError("Informe a chave de API.")
    if provider == "openai":
        return _openai_models(api_key)
    if provider == "openwebui":
        if not base_url:
            raise ProviderError("Informe a URL base do OpenWebUI.")
        return _openwebui_models(api_key, base_url)
    raise ProviderError(f"Provider desconhecido: {provider}")
