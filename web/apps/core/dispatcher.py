"""Dispacha o pipeline em background com fallback para thread local quando o broker nao responde.

Regra: o request nunca fica bloqueado. O usuario recebe a URL de acompanhamento
imediatamente e a pagina HTMX faz polling no estado do job.
"""
from __future__ import annotations

import logging
import os
import threading

from kombu.exceptions import OperationalError as CeleryBrokerError

from .tasks import process_search_job

logger = logging.getLogger(__name__)


def _run_inline(search_job_id: int) -> None:
    """Roda a task sincronamente dentro de uma thread (sem Celery)."""
    from django.db import connection
    try:
        process_search_job.apply(args=[search_job_id])
    except Exception:  # noqa: BLE001
        logger.exception("Falha rodando task inline para job %s", search_job_id)
    finally:
        # Evita deixar conexao DB aberta na thread auxiliar.
        try:
            connection.close()
        except Exception:  # noqa: BLE001
            pass


def dispatch_search_job(search_job_id: int) -> tuple[str, str]:
    """Enfileira o job.

    Retorna (modo, task_id_ou_thread_name).

    Modos:
      - "celery": publicado no broker (Redis), worker separado processa
      - "thread": rodando em thread daemon neste processo (fallback)
    """
    forcar_thread = os.environ.get("CELERY_EAGER", "0") == "1"

    if not forcar_thread:
        try:
            task = process_search_job.delay(search_job_id)
            return "celery", task.id or ""
        except CeleryBrokerError as exc:
            logger.warning("Broker Celery indisponivel (%s); caindo para thread local.", exc)
        except Exception:  # noqa: BLE001
            logger.exception("Erro inesperado ao publicar no broker; caindo para thread.")

    t = threading.Thread(
        target=_run_inline,
        args=(search_job_id,),
        name=f"search-job-{search_job_id}",
        daemon=True,
    )
    t.start()
    return "thread", t.name
