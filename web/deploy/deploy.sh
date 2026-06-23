#!/usr/bin/env bash
# Atualiza uma instalacao ja existente do IOMAT em /srv/iomat.
# Uso: sudo -u iomat bash deploy/deploy.sh   (e tenha sudo p/ reiniciar servicos)
set -euo pipefail

RAIZ="/srv/iomat"
cd "$RAIZ"

echo ">> git pull"
git pull --ff-only

cd "$RAIZ/web"
echo ">> dependencias"
. .venv/bin/activate
pip install -r requirements.txt --quiet

echo ">> migrate"
python manage.py migrate --noinput

echo ">> collectstatic"
python manage.py collectstatic --noinput

echo ">> reiniciando servicos"
sudo systemctl restart gunicorn-iomat celery-iomat

echo ">> OK. Status:"
systemctl --no-pager --lines=3 status gunicorn-iomat celery-iomat || true
