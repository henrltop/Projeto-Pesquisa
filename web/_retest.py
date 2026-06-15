"""Re-testa o prompt refinado nos docs com gabarito humano, COM contexto.
Nao persiste: so mede concordancia para comparar com as rodadas anteriores."""
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()
from django.contrib.auth import get_user_model
from apps.documents.models import Document, Classification
from apps.reviews.models import Review
from apps.core.contexto import montar_contexto
from apps.core.openai_client import OpenAIClassifier
try:
    from apps.validations.models import BlindItem
except Exception:
    BlindItem = None

def bin_ia(c): return "rel" if c in {"super_relevante","relevante"} else "nao"
def bin_h(d): return "rel" if d in {"super_relevante","aprovado","ressalva"} else "nao"

humano = {}
if BlindItem:
    for it in BlindItem.objects.exclude(decisao_humana="").exclude(decisao_humana__isnull=True).order_by("created_at"):
        humano[it.document_id] = it.decisao_humana
for r in Review.objects.order_by("created_at"):
    humano.setdefault(r.document_id, r.decisao)

# docs com gabarito + ja tem versao com_contexto (entao sabemos que tem texto e vizinhas)
docs = (Document.objects.filter(classificacoes__com_contexto=True).distinct())
casos = [d for d in docs if d.pk in humano]

User = get_user_model()
u = User.objects.filter(is_superuser=True).first() or User.objects.first()
prof = u.profile
clf = OpenAIClassifier(api_key=prof.get_openai_key(), model=prof.modelo_efetivo, base_url=prof.base_url_efetivo)

cache = {}
ok_novo = 0
ok_antigo_ctx = 0
n = 0
linhas = []
for d in casos:
    h = humano[d.pk]
    bh = bin_h(h)
    old_ctx = d.classificacoes.filter(com_contexto=True).order_by("-created_at").first()
    try:
        ctx = montar_contexto(tipo_edicao=d.tipo_edicao, edicao_id=d.edicao_id,
                              pagina=d.pagina, texto_alvo=d.texto_bruto or "", cap=5, cache=cache)
        res = clf.classificar(ctx["texto"], "ensino profissional", multipagina=True)
    except Exception as e:
        linhas.append(f"  doc {d.pk}: ERRO {e}")
        continue
    n += 1
    novo = res.classificacao
    antigo = old_ctx.classificacao
    if bin_ia(novo) == bh: ok_novo += 1
    if bin_ia(antigo) == bh: ok_antigo_ctx += 1
    marca = "OK" if bin_ia(novo)==bh else "X"
    linhas.append(f"  doc {d.pk} ({d.ano}): ctx_antigo={antigo} -> ctx_NOVO={novo} | humano={h} [{marca}]")

out = []
out.append(f"docs testados: {n}")
if n:
    out.append(f"concordancia COM contexto (prompt ANTIGO): {ok_antigo_ctx}/{n} = {100*ok_antigo_ctx/n:.1f}%")
    out.append(f"concordancia COM contexto (prompt NOVO):   {ok_novo}/{n} = {100*ok_novo/n:.1f}%")
    out.append(f"variacao do refino: {100*(ok_novo-ok_antigo_ctx)/n:+.1f} pontos")
out.append("\ndetalhe:")
out += linhas
open("_retest_out.txt","w",encoding="utf-8").write("\n".join(out)+"\n")
