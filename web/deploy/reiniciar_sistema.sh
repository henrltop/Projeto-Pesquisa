#!/usr/bin/env bash
# reiniciar_sistema — reinicia o site IOMAT (Gunicorn + worker Celery).
# Instale como comando global (ver deploy/README.md) e rode: reiniciar_sistema
set -euo pipefail

echo ">> Reiniciando o site (gunicorn-iomat + celery-iomat)..."
sudo systemctl restart gunicorn-iomat celery-iomat

echo ">> Status:"
systemctl --no-pager --lines=3 status gunicorn-iomat celery-iomat || true

echo ">> Site reiniciado."
