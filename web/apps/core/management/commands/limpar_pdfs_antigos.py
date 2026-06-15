"""Remove PDFs baixados sob demanda (auditoria) que ficaram 2+ dias sem uso.

Politica:
- PDFs do CORPUS (relevantes/duvidosos, referenciados em Document.caminho_pdf) sao
  PERMANENTES e nunca removidos.
- Os demais PDFs em media/pdfs (paginas de contexto e paginas de irrelevantes
  baixadas para visualizacao) sao temporarios. Cada visualizacao "renova" o arquivo
  (atualiza o mtime). Este comando apaga os que passaram do prazo sem serem abertos.

Uso:
  python manage.py limpar_pdfs_antigos                 # apaga > 2 dias sem uso
  python manage.py limpar_pdfs_antigos --dias 7        # outro prazo
  python manage.py limpar_pdfs_antigos --dry-run       # so mostra o que apagaria
"""
from __future__ import annotations

import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.documents.models import Document


class Command(BaseCommand):
    help = "Apaga PDFs temporarios (nao-corpus) parados ha N dias (default 2)."

    def add_arguments(self, parser):
        parser.add_argument("--dias", type=float, default=2.0,
                            help="prazo minimo de retencao em dias (default 2)")
        parser.add_argument("--dry-run", action="store_true",
                            help="nao apaga; so lista o que seria removido")

    def handle(self, *args, **opts):
        pdf_dir = Path(settings.MEDIA_ROOT) / "pdfs"
        if not pdf_dir.exists():
            self.stdout.write("Pasta media/pdfs nao existe; nada a fazer.")
            return

        # PDFs do corpus (permanentes): basename de cada caminho_pdf preenchido.
        corpus = {
            Path(c).name
            for c in Document.objects.exclude(caminho_pdf="").values_list("caminho_pdf", flat=True)
        }

        limite = opts["dias"] * 86400
        agora = time.time()
        dry = opts["dry_run"]

        total = apagados = preservados_corpus = mantidos_recentes = 0
        bytes_liberados = 0
        for f in pdf_dir.glob("*.pdf"):
            total += 1
            if f.name in corpus:
                preservados_corpus += 1
                continue
            idade = agora - f.stat().st_mtime
            if idade < limite:
                mantidos_recentes += 1
                continue
            tam = f.stat().st_size
            if dry:
                self.stdout.write(f"  [dry] apagaria {f.name} (idade {idade/86400:.1f}d)")
            else:
                try:
                    f.unlink()
                except OSError as e:
                    self.stderr.write(f"  erro ao apagar {f.name}: {e}")
                    continue
            apagados += 1
            bytes_liberados += tam

        self.stdout.write(self.style.SUCCESS(
            f"{'[DRY-RUN] ' if dry else ''}Total={total} | corpus_preservado={preservados_corpus} "
            f"| recentes_mantidos={mantidos_recentes} | apagados={apagados} "
            f"| liberado={bytes_liberados/1024/1024:.1f} MB"
        ))
