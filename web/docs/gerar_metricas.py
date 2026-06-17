"""Gera as metricas de avaliacao dos modelos locais contra o GABARITO HUMANO.

GABARITO (referencia): a **validacao humana** registrada na tabela `Review`.
A decisao do revisor e a verdade, tenha ele concordado ou discordado da
sugestao da IA -- concordar e validar; discordar e justificar tambem e validar.

Modo secundario (--gabarito=modelo): usa a classificacao do modelo de
referencia (GABARITO_MODELO) como gabarito. Util so para comparacao; nos
artefatos do artigo o nome desse modelo nao e citado.

O script NAO modifica o banco: apenas le e escreve arquivos em docs/dados/.

Uso (a partir de web/, com o venv ativo):
    python docs/gerar_metricas.py                 # gabarito = humano (padrao)
    python docs/gerar_metricas.py --gabarito=modelo

Saidas (docs/dados/): comparativo_tidy.csv, distribuicao_classes.csv,
metricas_modelos.csv, matrizes_confusao.json, resumo.json
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap do Django (o script vive em web/docs/, o projeto esta em web/)
# ---------------------------------------------------------------------------
WEB_DIR = Path(__file__).resolve().parent.parent          # .../web
DOCS_DIR = Path(__file__).resolve().parent                # .../web/docs
DADOS_DIR = DOCS_DIR / "dados"
DADOS_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(WEB_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

try:                                  # stdout em utf-8 (Windows usa cp1252)
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

import django  # noqa: E402

django.setup()

from django.db.models import Count  # noqa: E402

from apps.documents.models import Document  # noqa: E402
from apps.documents.models import Classification  # noqa: E402
from apps.reviews.models import Review  # noqa: E402
from apps.searches.models import PipelineStage, SearchJob  # noqa: E402

# ---------------------------------------------------------------------------
# Configuracao
# ---------------------------------------------------------------------------
# Modelo de referencia (usado so no modo --gabarito=modelo e na concordancia
# auxiliar). Validado por humano; nao citado no artigo.
GABARITO_MODELO = "gpt-5.4-mini"

# Ignora jobs de teste (poucos documentos classificados).
MIN_CLASSIF = 30

# Classes de relevancia da IA (a classe 'erro' = falha de formato, fica fora).
CLASSES_MULTI = ["super_relevante", "relevante", "duvidoso", "irrelevante"]
RELEVANTES = {"super_relevante", "relevante"}
NAO_RELEVANTES = {"duvidoso", "irrelevante"}


def bin_ia(classe: str | None) -> str | None:
    """Binariza uma classe da IA. 'erro'/desconhecida -> None (descarta)."""
    if classe in RELEVANTES:
        return "relevante"
    if classe in NAO_RELEVANTES:
        return "nao_relevante"
    return None


def bin_humano(decisao: str) -> str | None:
    """Binariza a decisao do revisor humano (tabela Review).

    super_relevante / aprovado / ressalva -> relevante ; rejeitado -> nao.
    """
    if decisao in {"super_relevante", "aprovado", "ressalva"}:
        return "relevante"
    if decisao == "rejeitado":
        return "nao_relevante"
    return None


# ---------------------------------------------------------------------------
# Selecao de dados
# ---------------------------------------------------------------------------
def classes_por_doc(job: SearchJob) -> dict[int, str]:
    """doc_id -> classe (a classificacao mais recente daquele doc no job)."""
    out: dict[int, str] = {}
    for doc_id, classe in (
        Classification.objects.filter(search_job=job)
        .order_by("created_at")
        .values_list("document_id", "classificacao")
    ):
        out[doc_id] = classe
    return out


def tempo_por_job(job: SearchJob) -> dict:
    """Tempo de processamento por documento naquele job.

    Usa a MEDIANA do intervalo entre classificacoes consecutivas (robusta a
    pausas/idle), descartando saltos > 1 h. E tempo fim-a-fim (inclui o
    delimitador e os downloads do IOMAT), nao inferencia pura do classificador.
    """
    import statistics

    times = list(
        Classification.objects.filter(search_job=job)
        .order_by("created_at").values_list("created_at", flat=True)
    )
    deltas = [
        (times[i + 1] - times[i]).total_seconds() for i in range(len(times) - 1)
    ]
    deltas = [d for d in deltas if 0 < d < 3600]
    mediana = statistics.median(deltas) if deltas else None
    stage = PipelineStage.objects.filter(search_job=job, codigo="classificacao").first()
    total = stage.duracao_segundos if stage else None
    return {"mediana_doc_seg": mediana, "total_stage_seg": total, "n": len(times)}


def gabarito_humano() -> dict[int, str]:
    """doc_id -> decisao humana (review mais recente do documento)."""
    out: dict[int, str] = {}
    for doc_id, decisao in (
        Review.objects.order_by("created_at").values_list("document_id", "decisao")
    ):
        out[doc_id] = decisao
    return out


def escolher_jobs() -> tuple[SearchJob | None, dict[str, SearchJob]]:
    """Retorna (job_do_modelo_referencia, {modelo_local: job_mais_recente})."""
    jobs = list(SearchJob.objects.order_by("-created_at"))
    info: dict[int, tuple[str, int]] = {}
    for par in (
        Classification.objects.values("search_job_id", "modelo_ia")
        .annotate(n=Count("id"))
        .order_by("-n")
    ):
        jid = par["search_job_id"]
        if jid is not None and jid not in info:
            info[jid] = (par["modelo_ia"], par["n"])

    gab_jobs = [
        (j, info[j.id][1]) for j in jobs
        if j.id in info and info[j.id][0] == GABARITO_MODELO
    ]
    job_ref = max(gab_jobs, key=lambda x: x[1])[0] if gab_jobs else None

    escolha: dict[str, SearchJob] = {}
    for j in jobs:  # mais recente primeiro
        if j.id not in info:
            continue
        modelo, n = info[j.id]
        if modelo == GABARITO_MODELO or n < MIN_CLASSIF:
            continue
        escolha.setdefault(modelo, j)
    return job_ref, escolha


# ---------------------------------------------------------------------------
# Metricas binarias
# ---------------------------------------------------------------------------
def metricas_binarias(pares: list[tuple[str, str]]) -> dict:
    """pares = [(bin_gabarito, bin_modelo)]. Classe positiva = 'relevante'."""
    tp = fp = fn = tn = 0
    for g, m in pares:
        if g == "relevante" and m == "relevante":
            tp += 1
        elif g == "nao_relevante" and m == "relevante":
            fp += 1
        elif g == "relevante" and m == "nao_relevante":
            fn += 1
        else:
            tn += 1
    n = tp + fp + fn + tn
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    acc = (tp + tn) / n if n else 0.0
    return {
        "n": n, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precisao": prec, "recall": rec, "f1": f1, "acuracia": acc,
        "matriz": [[tn, fp], [fn, tp]],  # linhas=gabarito, cols=modelo
        "labels": ["nao_relevante", "relevante"],
    }


def concordancia_ref_vs_humano(job_ref: SearchJob | None, humano: dict[int, str]) -> dict:
    """Quanto o modelo de referencia (gpt-mini) concorda com o humano (binario)."""
    if job_ref is None:
        return {"n": 0, "concordancia": None}
    ref = classes_por_doc(job_ref)
    n = c = 0
    for doc_id, classe in ref.items():
        bh, bg = bin_humano(humano.get(doc_id, "")), bin_ia(classe)
        if bh is None or bg is None:
            continue
        n += 1
        c += int(bh == bg)
    return {"n": n, "concordancia": c / n if n else None, "job_id": job_ref.id}


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def main() -> None:
    modo = "humano"
    for arg in sys.argv[1:]:
        if arg.startswith("--gabarito="):
            modo = arg.split("=", 1)[1].strip()

    job_ref, jobs_modelos = escolher_jobs()
    humano = gabarito_humano()

    if modo == "modelo":
        if job_ref is None:
            raise SystemExit("Sem job do modelo de referencia para usar como gabarito.")
        gab = classes_por_doc(job_ref)
        gab_bin = {d: bin_ia(c) for d, c in gab.items()}
        gab_fonte = f"modelo de referencia (job #{job_ref.id})"
        n_gab = len(gab_bin)
    else:  # humano (padrao)
        gab_bin = {d: bin_humano(dec) for d, dec in humano.items()}
        gab_fonte = "validacao humana (tabela Review)"
        n_gab = sum(1 for v in gab_bin.values() if v is not None)

    print(f"GABARITO: {gab_fonte} -> {n_gab} docs com rotulo binario")
    print("MODELOS AVALIADOS:")
    for modelo, j in jobs_modelos.items():
        print(f"  {modelo:16s} job #{j.id} (status={j.status})")

    docmeta = {
        d.id: (d.ano, d.edicao_id, d.pagina)
        for d in Document.objects.only("id", "ano", "edicao_id", "pagina")
    }

    tidy_rows: list[dict] = []
    dist_rows: list[dict] = []
    metr_rows: list[dict] = []
    matrizes: dict[str, dict] = {}

    for modelo, job in jobs_modelos.items():
        mod = classes_por_doc(job)
        dist_m = Counter(mod.values())
        dist_rows.append({
            "modelo": modelo,
            **{c: dist_m.get(c, 0) for c in CLASSES_MULTI},
            "erro": dist_m.get("erro", 0),
        })
        n_erro = dist_m.get("erro", 0)
        n_modelo_total = len(mod)

        pares_bin: list[tuple[str, str]] = []
        for doc_id, bg in gab_bin.items():
            if bg is None:
                continue
            cm = mod.get(doc_id)
            bm = bin_ia(cm) if cm else None
            ano, edicao, pagina = docmeta.get(doc_id, (None, "", None))
            if bm is not None:
                pares_bin.append((bg, bm))
            tidy_rows.append({
                "doc_id": doc_id, "ano": ano, "edicao_id": edicao, "pagina": pagina,
                "modelo": modelo, "job_id": job.id,
                "gabarito_bin": bg,
                "modelo_classe": cm or "", "modelo_bin": bm or "",
                "acertou_bin": int(bg == bm) if bm else "",
            })

        mb = metricas_binarias(pares_bin)
        tempo = tempo_por_job(job)
        matrizes[modelo] = {"binaria": mb, "n_erros": n_erro}
        metr_rows.append({
            "modelo": modelo, "job_id": job.id, "status_job": job.status,
            "n_referencia": n_gab, "n_avaliado": mb["n"],
            "cobertura": mb["n"] / n_gab if n_gab else 0.0,
            "taxa_erro": n_erro / n_modelo_total if n_modelo_total else 0.0,
            "precisao": mb["precisao"], "recall": mb["recall"], "f1": mb["f1"],
            "acuracia": mb["acuracia"],
            "tempo_mediano_doc_seg": tempo["mediana_doc_seg"],
            "tempo_total_stage_seg": tempo["total_stage_seg"],
        })

    # composicao do gabarito humano (decisoes originais + binario)
    comp_humano = Counter(humano.values())
    comp_bin = Counter(v for v in gab_bin.values() if v is not None)
    aux = concordancia_ref_vs_humano(job_ref, humano)

    # ----- escreve arquivos -----
    _escreve_csv(DADOS_DIR / "comparativo_tidy.csv", tidy_rows)
    _escreve_csv(DADOS_DIR / "distribuicao_classes.csv", dist_rows)
    _escreve_csv(DADOS_DIR / "metricas_modelos.csv", metr_rows)
    with open(DADOS_DIR / "matrizes_confusao.json", "w", encoding="utf-8") as fh:
        json.dump(matrizes, fh, ensure_ascii=False, indent=2)

    corpus_n = len(classes_por_doc(job_ref)) if job_ref else max(
        (len(classes_por_doc(j)) for j in jobs_modelos.values()), default=0
    )

    resumo = {
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "modo_gabarito": modo,
        "corpus_n_docs": corpus_n,
        "gabarito": {
            "fonte": gab_fonte, "n_docs": n_gab,
            "composicao_decisoes": dict(comp_humano),
            "composicao_binaria": dict(comp_bin),
        },
        "referencia_auxiliar": {
            "descricao": "concordancia binaria do modelo-assistente com o humano",
            **aux,
        },
        "classes_multi": CLASSES_MULTI,
        "modelos": metr_rows,
        "distribuicao": dist_rows,
        "matrizes": matrizes,
    }
    with open(DADOS_DIR / "resumo.json", "w", encoding="utf-8") as fh:
        json.dump(resumo, fh, ensure_ascii=False, indent=2)

    # ----- resumo no terminal -----
    print(f"\nGabarito humano: {comp_bin.get('relevante', 0)} relevantes / "
          f"{comp_bin.get('nao_relevante', 0)} nao-relevantes "
          f"(decisoes: {dict(comp_humano)})")
    print("\n=== METRICAS (binario, vs validacao humana) ===")
    print(f"{'modelo':16s} {'cob.':>5s} {'erro':>5s} {'prec':>5s} {'rec':>5s} {'F1':>6s} {'acc':>5s} {'t/doc':>7s}")
    for r in metr_rows:
        t = r["tempo_mediano_doc_seg"]
        tstr = f"{t:.0f}s" if t else "n/d"
        print(f"{r['modelo']:16s} {r['cobertura']*100:4.0f}% {r['taxa_erro']*100:4.0f}% "
              f"{r['precisao']:.2f}  {r['recall']:.2f}  {r['f1']:.2f}  {r['acuracia']:.2f}  {tstr:>7s}")
    if aux["concordancia"] is not None:
        print(f"\n(aux.) modelo-assistente x humano: {aux['concordancia']*100:.1f}% "
              f"em {aux['n']} docs")
    print(f"\nArquivos salvos em: {DADOS_DIR}")


def _escreve_csv(caminho: Path, linhas: list[dict]) -> None:
    import csv
    if not linhas:
        return
    with open(caminho, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)


if __name__ == "__main__":
    main()
