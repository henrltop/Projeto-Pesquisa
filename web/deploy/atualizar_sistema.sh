#!/usr/bin/env bash
# atualizar_sistema — atualiza o IOMAT com o que estiver no git e reinicia.
#   git pull -> dependencias -> migracoes -> arquivos estaticos -> restart
# Instale como comando global (ver deploy/README.md) e rode: atualizar_sistema
#
# Requer permissao de sudo (troca para o usuario 'iomat' no codigo e reinicia
# os servicos systemd).
set -euo pipefail

RAIZ="/srv/iomat"
APP="$RAIZ/web"

echo ">> [1/5] Baixando alteracoes do git..."
sudo -u iomat git -C "$RAIZ" pull --ff-only

echo ">> [2/5] Instalando dependencias (pip)..."
sudo -u iomat bash -c "cd '$APP' && . .venv/bin/activate && pip install -r requirements.txt --quiet"

echo ">> [3/5] Aplicando migracoes do banco..."
sudo -u iomat bash -c "cd '$APP' && . .venv/bin/activate && python manage.py migrate --noinput"

echo ">> [4/5] Coletando arquivos estaticos..."
sudo -u iomat bash -c "cd '$APP' && . .venv/bin/activate && python manage.py collectstatic --noinput"

echo ">> [5/5] Reiniciando servicos..."
sudo systemctl restart gunicorn-iomat celery-iomat

echo ">> Status:"
systemctl --no-pager --lines=3 status gunicorn-iomat celery-iomat || true

echo ">> Sistema atualizado."
