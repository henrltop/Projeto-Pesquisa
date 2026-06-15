"""Reprocessa documentos ja classificados, agora COM contexto multipagina.

Mantem as classificacoes antigas (com_contexto=False) e cria novas
(com_contexto=True) ao lado, permitindo comparar o efeito do contexto.

Uso:
  python manage.py reclassificar_com_contexto --user henri
  python manage.py reclassificar_com_contexto --limit 20 --dry-run
"""
from __future__ import annotations

import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.core.contexto import montar_contexto
from apps.core.openai_client import OpenAIClassifier
from apps.documents.models import Classification, Document


class Command(BaseCommand):
    help = "Reclassifica documentos com contexto multipagina (mantendo as antigas)."

    def add_arguments(self, parser):
        parser.add_argument("--user", type=str, default=None,
                            help="username dono da chave de IA (padrao: primeiro com chave)")
        parser.add_argument("--limit", type=int, default=0, help="maximo de docs (0 = todos)")
        parser.add_argument("--cap", type=int, default=5, help="teto de paginas de contexto por lado")
        parser.add_argument("--dry-run", action="store_true", help="nao chama a IA nem salva; so mostra o plano")
        parser.add_argument("--ano-min", type=int, default=None)
        parser.add_argument("--ano-max", type=int, default=None)

    def handle(self, *args, **opts):
        User = get_user_model()

        # --- resolve usuario / chave ---
        if opts["user"]:
            try:
                user = User.objects.get(username=opts["user"])
            except User.DoesNotExist:
                raise CommandError(f"Usuario '{opts['user']}' nao encontrado.")
        else:
            user = None
            for u in User.objects.all():
                prof = getattr(u, "profile", None)
                if prof and prof.get_openai_key():
                    user = u
                    break
            if not user:
                raise CommandError("Nenhum usuario com chave de IA configurada.")

        profile = user.profile
        api_key = profile.get_openai_key()
        if not api_key:
            raise CommandError(f"Usuario '{user.username}' nao tem chave de IA.")
        modelo = profile.modelo_efetivo
        base_url = profile.base_url_efetivo
        self.stdout.write(f"Usuario={user.username} modelo={modelo}")

        # --- seleciona docs: tem classificacao antiga, ainda sem versao com contexto ---
        ja_feitos = set(
            Classification.objects.filter(com_contexto=True).values_list("document_id", flat=True)
        )
        qs = (
            Document.objects
            .exclude(texto_bruto="")
            .filter(classificacoes__com_contexto=False)
            .distinct()
        )
        if opts["ano_min"]:
            qs = qs.filter(ano__gte=opts["ano_min"])
        if opts["ano_max"]:
            qs = qs.filter(ano__lte=opts["ano_max"])
        docs = [d for d in qs.order_by("ano", "edicao_id", "pagina") if d.pk not in ja_feitos]
        if opts["limit"]:
            docs = docs[: opts["limit"]]

        total = len(docs)
        self.stdout.write(f"Documentos a reprocessar: {total} (ja feitos antes: {len(ja_feitos)})")
        if opts["dry_run"]:
            self.stdout.write(self.style.WARNING("DRY-RUN: nenhuma chamada de IA sera feita."))
            for d in docs[:10]:
                self.stdout.write(f"  - doc {d.pk} ano={d.ano} ed={d.edicao_id} pag={d.pagina}")
            return
        if total == 0:
            self.stdout.write(self.style.SUCCESS("Nada a fazer."))
            return

        classifier = OpenAIClassifier(api_key=api_key, model=modelo, base_url=base_url)
        cache: dict = {}
        cap = opts["cap"]

        mudou = 0
        igual = 0
        erros = 0
        t0 = time.time()

        for i, doc in enumerate(docs, 1):
            antiga = (
                doc.classificacoes.filter(com_contexto=False).order_by("-created_at").first()
            )
            termo = (antiga.termo_buscado if antiga else "") or "ensino tecnologico"
            classe_antiga = antiga.classificacao if antiga else "?"

            try:
                ctx = montar_contexto(
                    tipo_edicao=doc.tipo_edicao,
                    edicao_id=doc.edicao_id,
                    pagina=doc.pagina,
                    texto_alvo=doc.texto_bruto or "",
                    cap=cap,
                    cache=cache,
                )
                c = classifier.classificar(ctx["texto"], termo, multipagina=True)
            except Exception as exc:  # noqa: BLE001
                erros += 1
                self.stderr.write(f"  [{i}/{total}] doc {doc.pk} ERRO: {exc}")
                continue

            Classification.objects.create(
                document=doc,
                search_job=None,
                termo_buscado=termo,
                classificacao=c.classificacao,
                tipo_ato=c.tipo_ato,
                justificativa=c.justificativa,
                prompt_enviado=c.prompt_usuario,
                resposta_crua=c.resposta_crua,
                modelo_ia=classifier.model,
                tokens_input=c.tokens_input,
                tokens_output=c.tokens_output,
                com_contexto=True,
                paginas_contexto=",".join(str(p) for p in ctx["paginas"]),
            )

            if c.classificacao == classe_antiga:
                igual += 1
                marca = "="
            else:
                mudou += 1
                marca = "MUDOU"
            extra = ""
            if len(ctx["paginas"]) > 1:
                extra = f" [ctx: {ctx['paginas']}]"
            self.stdout.write(
                f"  [{i}/{total}] doc {doc.pk} ({doc.ano}): {classe_antiga} -> {c.classificacao} {marca}{extra}"
            )

            if i % 10 == 0:
                dt = time.time() - t0
                vel = i / dt if dt else 0
                eta = (total - i) / vel if vel else 0
                self.stdout.write(
                    self.style.HTTP_INFO(
                        f"    ...{i}/{total} | mudou={mudou} igual={igual} erros={erros} "
                        f"| {vel:.2f} doc/s | ETA {eta/60:.1f} min"
                    )
                )

        dt = time.time() - t0
        self.stdout.write(self.style.SUCCESS(
            f"\nConcluido em {dt/60:.1f} min. "
            f"Total={total} mudou={mudou} igual={igual} erros={erros}"
        ))
        if mudou + igual:
            pct = 100 * mudou / (mudou + igual)
            self.stdout.write(f"Taxa de mudanca pela adicao de contexto: {pct:.1f}%")
        self.stdout.write("Gere o comparativo com: python manage.py relatorio_contexto")
