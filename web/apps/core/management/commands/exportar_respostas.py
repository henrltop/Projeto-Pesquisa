"""Exporta TODAS as classificacoes (com a resposta bruta da IA) para um CSV.

Serve para analisar a veracidade das respostas e montar o benchmark de modelos
em outra maquina, ja que o banco SQLite nao vai para o git.

Uso:
  python manage.py exportar_respostas
  python manage.py exportar_respostas --saida dados_exportados/respostas.csv
"""
from __future__ import annotations

import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.documents.models import Classification


class Command(BaseCommand):
    help = "Exporta as classificacoes + respostas brutas da IA para CSV (analise/benchmark)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--saida", type=str, default="dados_exportados/respostas_brutas.csv",
            help="caminho do CSV de saida (relativo a pasta web/)",
        )

    def handle(self, *args, **opts):
        saida = Path(opts["saida"])
        saida.parent.mkdir(parents=True, exist_ok=True)

        cols = [
            "classificacao_id", "busca_id", "termo", "modelo_ia",
            "doc_id", "ano", "edicao", "pagina",
            "classificacao", "tipo_ato", "justificativa",
            "com_contexto", "paginas_contexto", "tokens_input", "tokens_output",
            "created_at", "resposta_crua",
        ]
        qs = (
            Classification.objects
            .select_related("document", "search_job")
            .order_by("search_job_id", "document_id")
        )
        total = qs.count()
        with open(saida, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for c in qs.iterator():
                d = c.document
                w.writerow({
                    "classificacao_id": c.id,
                    "busca_id": c.search_job_id or "",
                    "termo": c.termo_buscado,
                    "modelo_ia": c.modelo_ia,
                    "doc_id": d.id,
                    "ano": d.ano,
                    "edicao": d.edicao_id,
                    "pagina": d.pagina,
                    "classificacao": c.classificacao,
                    "tipo_ato": c.tipo_ato,
                    "justificativa": c.justificativa,
                    "com_contexto": c.com_contexto,
                    "paginas_contexto": c.paginas_contexto,
                    "tokens_input": c.tokens_input or "",
                    "tokens_output": c.tokens_output or "",
                    "created_at": c.created_at.isoformat(),
                    "resposta_crua": c.resposta_crua,
                })
        self.stdout.write(self.style.SUCCESS(
            f"Exportadas {total} classificacoes para {saida}"
        ))
