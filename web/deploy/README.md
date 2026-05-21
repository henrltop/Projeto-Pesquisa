# Deploy - IOMAT Web

> Preenchido completamente na Fase E. Por ora, um esqueleto do que vem.

## Alvo

VPS Ubuntu 22.04/24.04 LTS com:
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Nginx
- systemd (para Gunicorn e Celery)
- certbot (Let's Encrypt)

## Arquivos desta pasta

- `gunicorn-iomat.service` *(Fase E)* - unit systemd do Gunicorn
- `celery-iomat.service` *(Fase E)* - unit systemd do worker Celery
- `nginx.conf` *(Fase E)* - server block do Nginx
- `deploy.sh` *(Fase E)* - script de bootstrap

## Passo a passo (resumo)

1. `apt install python3-venv postgresql redis nginx`
2. Criar usuario do sistema `iomat` e clonar o repo em `/srv/iomat`
3. `python -m venv .venv && pip install -r web/requirements.txt`
4. `createdb iomat` e configurar usuario Postgres
5. `cp .env.example .env` e preencher com chaves reais
6. `python manage.py migrate && collectstatic`
7. Copiar units em `deploy/` para `/etc/systemd/system/` e habilitar
8. Copiar `nginx.conf` para `/etc/nginx/sites-available/` e linkar
9. `certbot --nginx -d seudominio.com`
