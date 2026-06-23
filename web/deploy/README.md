# Deploy — IOMAT Mineração

Runbook para subir o sistema em um servidor **Ubuntu 24.04** próprio (ex.: a
máquina da faculdade com a GPU/Ollama), **exposto na internet com HTTPS**, modo
**nativo** (systemd + Gunicorn + Nginx). Banco **PostgreSQL** (obrigatório — a
busca full-text não funciona em SQLite).

## Arquivos desta pasta

| Arquivo | Para quê |
|---|---|
| `gunicorn-iomat.service` | unit systemd do Gunicorn (Django/WSGI) |
| `celery-iomat.service` | unit systemd do worker Celery (classificação) |
| `nginx.conf` | server block do Nginx (proxy reverso) |
| `deploy.sh` | script de atualização (`git pull` + migrate + restart) |

---

## 1. Pacotes do sistema

```bash
sudo apt update && sudo apt install -y \
    python3-venv python3-dev build-essential libpq-dev \
    postgresql postgresql-contrib redis-server nginx git certbot python3-certbot-nginx
```

> O Ollama já está instalado nesta máquina; nada a fazer quanto a ele aqui.

## 2. Usuário de sistema + código

```bash
sudo useradd --system --home-dir /srv/iomat --shell /bin/bash iomat
sudo install -d -o iomat -g iomat /srv/iomat
sudo -u iomat git clone https://github.com/henrltop/Projeto-Pesquisa.git /srv/iomat
```

## 3. PostgreSQL

```bash
sudo -u postgres psql -c "CREATE USER iomat WITH PASSWORD 'TROQUE_ISTO';"
sudo -u postgres psql -c "CREATE DATABASE iomat OWNER iomat;"
```

## 4. Ambiente virtual + dependências (como o usuário iomat)

```bash
sudo -u iomat bash
cd /srv/iomat/web
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

## 5. Configuração (`.env`)

```bash
cp .env.example .env
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # FIELD_ENCRYPTION_KEY
python -c "import secrets; print(secrets.token_urlsafe(50))"                                 # DJANGO_SECRET_KEY
nano .env
```

Conteúdo mínimo do `.env` em produção:

```ini
DJANGO_SETTINGS_MODULE=config.settings.prod
DJANGO_SECRET_KEY=<token gerado>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=seudominio.edu.br
POSTGRES_PASSWORD=<a senha do passo 3>
FIELD_ENCRYPTION_KEY=<a chave Fernet gerada>
REDIS_URL=redis://localhost:6379/0
# Ollama na propria maquina (sem o SSL do servidor 'tutoria'):
DELIMITADOR_BASE_URL=http://localhost:11434
```

> `DJANGO_SETTINGS_MODULE=config.settings.prod` é **obrigatório no `.env`**: o
> `config/celery.py` cai em `dev` (SQLite) se essa variável não estiver no
> ambiente do worker.

## 6. Migrar + estáticos + superusuário (banco limpo)

```bash
# manage.py usa settings.dev por padrao; force prod nesta shell:
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
exit   # sai do shell do usuario iomat
```

## 7. Serviços systemd (Gunicorn + Celery)

```bash
sudo cp /srv/iomat/web/deploy/gunicorn-iomat.service /etc/systemd/system/
sudo cp /srv/iomat/web/deploy/celery-iomat.service  /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn-iomat celery-iomat
systemctl status gunicorn-iomat celery-iomat   # devem estar "active (running)"
```

## 8. Nginx

```bash
sudo cp /srv/iomat/web/deploy/nginx.conf /etc/nginx/sites-available/iomat
sudo nano /etc/nginx/sites-available/iomat        # troque SEU_DOMINIO
sudo ln -s /etc/nginx/sites-available/iomat /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

## 9. HTTPS (Let's Encrypt)

```bash
sudo certbot --nginx -d seudominio.edu.br
```

> Faça o **certbot ANTES de testar o login**: o `prod.py` usa cookies `Secure`,
> então a sessão só funciona sob HTTPS.

## 10. Firewall (se houver ufw)

```bash
sudo ufw allow 'Nginx Full'   # libera 80 e 443
sudo ufw allow OpenSSH
```

---

## Atualizar depois (redeploy)

```bash
sudo -u iomat bash /srv/iomat/web/deploy/deploy.sh
```

## Pegadinhas / observações

- **GPU única**: o worker Celery roda com `--concurrency=1` (classificação é
  sequencial; evita disputa de VRAM).
- **Limite de 4 h do Celery**: `CELERY_TASK_TIME_LIMIT` no `base.py` é 4 h, mas
  buscas com modelos de raciocínio (gpt-oss) chegaram a **4h25**. Se for usar
  modelos lentos, aumente o limite no `base.py` (ou via `--time-limit` no unit).
- **Logs**: `journalctl -u gunicorn-iomat -f` e `journalctl -u celery-iomat -f`.
- **Modelos por usuário**: o classificador (modelo, base_url, chave) é
  configurado no **Perfil/Admin** do app, não no `.env`. Para apontar o
  classificador ao Ollama local, use a base URL local no perfil.
- **Trazer dados depois**: para carregar um dump,
  `python manage.py loaddata dados_exportados/dump_completo.json` (exige usar a
  **mesma `FIELD_ENCRYPTION_KEY`** que cifrou as chaves de API originais).
