# IOMAT Mineracao - Versao Web (Django)

Versao web do pipeline de mineracao IOMAT + IA, construida em Django para deploy em VPS.

> Esta pasta `web/` coexiste com a versao original em Streamlit (`app_iomat.py`) que fica no diretorio raiz.

## Stack

- Django 5 + HTMX (sem SPA, sem build step)
- Celery + Redis (pipeline assincrono)
- PostgreSQL (producao) / SQLite (dev)
- Gunicorn + Nginx (producao)
- Tailwind via CDN

## Funcionalidades (Fase A - fundacao)

- [x] Autenticacao individual de usuarios
- [x] Chave OpenAI cifrada por usuario (Fernet)
- [x] Modelo compartilhado de documentos e buscas (uma equipe)
- [x] Classificacao IA em 3 niveis: relevante / duvidoso / irrelevante
- [x] Fila de revisao manual para documentos duvidosos
- [x] Painel interno com contadores e buscas recentes
- [x] Pagina publica sem login com estatisticas
- [x] Admin do Django configurado
- [ ] Pipeline Celery realmente funcional *(Fase B)*
- [ ] Deploy systemd/nginx *(Fase E)*

## Setup local (Windows)

```bash
cd web
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edite .env se quiser, mas dev ja tem fallback razoavel
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse http://localhost:8000 (pagina publica) ou http://localhost:8000/app/ (apos login).

## Popular dados de demonstracao (opcional)

Cria 2 usuarios fake, 3 buscas historicas e ~60 documentos ja classificados (inclui duvidosos para a fila de revisao):

```bash
python manage.py seed_demo --limpar
# usuarios criados (senha demo12345): henrique, beatriz
```

## Rodando o pipeline real

O pipeline e executado por uma task Celery. Voce tem DUAS opcoes:

### Opcao A - sem Redis (modo "eager", bom para testar a logica)

```bash
# Bash/Git Bash:
CELERY_EAGER=1 python manage.py runserver
# PowerShell:
$env:CELERY_EAGER="1"; python manage.py runserver
```

Nesse modo a task roda na mesma thread do request. Bom para testar integracao com IOMAT + OpenAI, ruim para UX (a pagina fica "carregando" ate terminar).

### Opcao B - com Redis + worker separado (modo real)

```bash
# terminal 1: sobe redis
docker compose -f docker-compose.dev.yml up -d redis

# terminal 2: worker Celery
celery -A config worker -l info --concurrency=2

# terminal 3: servidor web
python manage.py runserver
```

Assim o pipeline roda em background e a tela `/buscas/<id>/` atualiza os contadores via HTMX a cada 2s.

## Setup com Postgres + Redis (via Docker)

```bash
cd web
docker compose -f docker-compose.dev.yml up -d
# Altere .env para DATABASES apontarem ao Postgres local e
# defina DJANGO_SETTINGS_MODULE=config.settings.base se quiser Postgres em dev.
```

## Gerando a chave de criptografia Fernet

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Cole o valor em `FIELD_ENCRYPTION_KEY` no `.env`. Em `settings/dev.py` ha uma chave de fallback SOMENTE para desenvolvimento.

## Rodando o worker Celery

```bash
# Em outro terminal
celery -A config worker -l info
```

## Estrutura

```
web/
  config/         settings, urls, celery
  apps/
    accounts/     login + chave OpenAI cifrada
    searches/     SearchJob (historico compartilhado)
    documents/    Document + classificacao IA
    reviews/      revisao humana dos duvidosos
    dashboard/    painel interno (logado)
    public/       pagina publica com estatisticas
    core/         cliente IOMAT, cliente OpenAI, tasks Celery
  templates/      HTML (Tailwind CDN + HTMX)
  static/css/     CSS complementar
  media/pdfs/     PDFs baixados (git-ignored)
  deploy/         systemd + nginx (preenchido na Fase E)
```

## Fluxo do pipeline (Fase B em diante)

1. Usuario loga e configura sua chave OpenAI no perfil
2. Cria uma Nova busca (termo, anos, busca exata)
3. Task Celery executa:
   - Fase 1: consulta API IOMAT e deduplica com o banco
   - Fase 2: classifica com GPT-4o-mini em 3 niveis
   - Salva PDFs dos relevantes e duvidosos em `/media/pdfs/`
4. Documentos duvidosos caem na fila `/revisao/` para avaliacao humana
5. Reprocessamento de uma mesma combinacao NUNCA sobrescreve revisoes finais

## Deploy em producao

Ver `deploy/README.md` (sera preenchido na Fase E com passo-a-passo para VPS Ubuntu + Nginx + Gunicorn + systemd).
