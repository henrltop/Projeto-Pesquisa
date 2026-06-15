"""Gera o comparativo: classificacao SEM contexto x COM contexto x humano.

Produz um CSV e imprime metricas no terminal.

Uso:
  python manage.py relatorio_contexto
  python manage.py relatorio_contexto --saida comparativo.csv
"""
from __future__ import annotations

import csv

from django.core.management.base import BaseCommand

from apps.documents.models import Classification, Document
from apps.reviews.models import Review

try:
    from apps.validations.models import ValidationItem
except Exception:  # noqa: BLE001
    ValidationItem = None


def bin_ia(classe: str) -> str:
    return "relevante" if classe in {"super_relevante", "relevante"} else "nao_relevante"


def bin_humano(decisao: str) -> str:
    return "relevante" if decisao in {"super_relevante", "aprovado", "ressalva"} else "nao_relevante"


class Command(BaseCommand):
    help = "Comparativo sem-contexto x com-contexto x humano."

    def add_arguments(self, parser):
        parser.add_argument("--saida", type=str, default="comparativo_contexto.csv")

    def handle(self, *args, **opts):
        # docs com as duas versoes
        docs = (
            Document.objects
            .filter(classificacoes__com_contexto=True)
            .filter(classificacoes__com_contexto=False)
            .distinct()
            .order_by("ano", "edicao_id", "pagina")
        )

        # ground truth humano: prioriza ValidationItem (snapshot), senao Review
        humano_por_doc: dict[int, str] = {}
        if ValidationItem is not None:
            for it in ValidationItem.objects.exclude(decisao_humana="").order_by("created_at"):
                humano_por_doc[it.document_id] = it.decisao_humana
        for r in Review.objects.order_by("created_at"):
            humano_por_doc.setdefault(r.document_id, r.decisao)

        linhas = []
        mudou = igual = 0
        transicoes: dict[tuple[str, str], int] = {}
        # metricas vs humano
        n_h = 0
        concorda_old = concorda_new = 0

        for doc in docs:
            old = doc.classificacoes.filter(com_contexto=False).order_by("-created_at").first()
            new = doc.classificacoes.filter(com_contexto=True).order_by("-created_at").first()
            if not old or not new:
                continue
            co, cn = old.classificacao, new.classificacao
            if co == cn:
                igual += 1
            else:
                mudou += 1
            transicoes[(co, cn)] = transicoes.get((co, cn), 0) + 1

            humano = humano_por_doc.get(doc.pk, "")
            bo, bn = bin_ia(co), bin_ia(cn)
            bh = bin_humano(humano) if humano else ""
            c_old = c_new = ""
            if humano:
                n_h += 1
                c_old = "sim" if bo == bh else "nao"
                c_new = "sim" if bn == bh else "nao"
                if bo == bh:
                    concorda_old += 1
                if bn == bh:
                    concorda_new += 1

            linhas.append({
                "doc_id": doc.pk, "ano": doc.ano, "edicao": doc.edicao_id, "pagina": doc.pagina,
                "termo": new.termo_buscado, "paginas_contexto": new.paginas_contexto,
                "classe_sem_contexto": co, "classe_com_contexto": cn,
                "mudou": "sim" if co != cn else "nao",
                "tipo_ato_sem": old.tipo_ato, "tipo_ato_com": new.tipo_ato,
                "humano": humano, "bin_sem": bo, "bin_com": bn, "bin_humano": bh,
                "concorda_sem": c_old, "concorda_com": c_new,
            })

        # --- escreve CSV ---
        if linhas:
            with open(opts["saida"], "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=list(linhas[0].keys()))
                w.writeheader()
                w.writerows(linhas)

        # --- imprime metricas ---
        total = mudou + igual
        self.stdout.write(self.style.SUCCESS(f"\n=== COMPARATIVO ({total} docs com as duas versoes) ==="))
        if total:
            self.stdout.write(f"Mudaram de classe: {mudou} ({100*mudou/total:.1f}%)")
            self.stdout.write(f"Mantiveram:        {igual} ({100*igual/total:.1f}%)")

        self.stdout.write("\nTransicoes mais comuns (sem -> com):")
        for (a, b), n in sorted(transicoes.items(), key=lambda x: -x[1])[:15]:
            seta = "  =" if a == b else "  ->"
            self.stdout.write(f"  {a}{seta} {b}: {n}")

        if n_h:
            self.stdout.write(self.style.SUCCESS(f"\n=== VS HUMANO ({n_h} docs com gabarito) ==="))
            self.stdout.write(f"Concordancia SEM contexto: {concorda_old}/{n_h} = {100*concorda_old/n_h:.1f}%")
            self.stdout.write(f"Concordancia COM contexto: {concorda_new}/{n_h} = {100*concorda_new/n_h:.1f}%")
            delta = 100*(concorda_new - concorda_old)/n_h
            sinal = "+" if delta >= 0 else ""
            self.stdout.write(self.style.HTTP_INFO(f"Variacao: {sinal}{delta:.1f} pontos percentuais"))
        else:
            self.stdout.write("\n(sem documentos com gabarito humano nas duas versoes)")

        if linhas:
            self.stdout.write(f"\nCSV salvo em: {opts['saida']}")
