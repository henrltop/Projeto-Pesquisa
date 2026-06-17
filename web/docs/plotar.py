"""Gera os gráficos a partir de docs/dados/ (saída do gerar_metricas.py).

Lê docs/dados/resumo.json e escreve PNGs estilizados em docs/graficos/.
Não acessa o banco. O gabarito é a validação humana (tabela Review).

Conjunto de figuras (descritas no README):
    01  Relevância: humano x modelos (binário, simplificado)
    02  Composição do gabarito humano (decisões originais)
    03  Precisão / Recall / F1
    04  Completude (classificados x falhas x não processados)
    05  Tempo por documento
    06  Matrizes de confusão

Uso:
    python docs/plotar.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import Normalize  # noqa: E402
import numpy as np  # noqa: E402

DOCS_DIR = Path(__file__).resolve().parent
DADOS_DIR = DOCS_DIR / "dados"
GRAF_DIR = DOCS_DIR / "graficos"
GRAF_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Tema
# ---------------------------------------------------------------------------
TINTA = "#1d3557"
TINTA2 = "#6c757d"
GRID = "#e9ecef"

VERDE = "#8cce8a"
CINZA = "#ced4da"
VERMELHO = "#bc4749"
TEAL = "#2a9d8f"
CINZA_CLARO = "#e9ecef"

PALETA_PRF = {"precisao": "#89c2d9", "recall": "#468faf", "f1": "#013a63"}
CORES_HUMANO = {
    "super_relevante": "#1b7837", "aprovado": "#8cce8a",
    "ressalva": "#f4a259", "rejeitado": "#bc4749",
}
ROTULO_HUMANO = {
    "super_relevante": "Super relevante", "aprovado": "Aprovado",
    "ressalva": "Ressalva", "rejeitado": "Rejeitado",
}


def _tema() -> None:
    plt.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white",
        "savefig.facecolor": "white", "axes.edgecolor": "#ced4da",
        "axes.linewidth": 1.0, "axes.grid": True, "axes.axisbelow": True,
        "grid.color": GRID, "grid.linewidth": 1.0,
        "axes.spines.top": False, "axes.spines.right": False,
        "font.family": "DejaVu Sans", "font.size": 11,
        "xtick.color": "#495057", "ytick.color": "#495057",
        "axes.labelcolor": "#495057", "figure.dpi": 160,
    })


def _cabecalho(ax, titulo: str, subtitulo: str = "") -> None:
    ax.text(0.0, 1.16, titulo, transform=ax.transAxes, fontsize=15.5,
            fontweight="bold", color=TINTA, va="top")
    if subtitulo:
        ax.text(0.0, 1.075, subtitulo, transform=ax.transAxes, fontsize=9.5,
                color=TINTA2, va="top")


def _so_grid_y(ax) -> None:
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", visible=True)


def _so_grid_x(ax) -> None:
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)


def carregar() -> dict:
    with open(DADOS_DIR / "resumo.json", encoding="utf-8") as fh:
        return json.load(fh)


def salvar(fig, nome: str) -> None:
    fig.savefig(GRAF_DIR / nome, dpi=160, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print(f"  -> {nome}")


def _dist_por_modelo(resumo: dict) -> dict[str, dict]:
    return {d["modelo"]: d for d in resumo["distribuicao"]}


# ---------------------------------------------------------------------------
def g_comparativo(resumo: dict) -> None:
    """01 - Relevância: o que o humano julgou x o que cada modelo classificou."""
    dist = _dist_por_modelo(resumo)
    ordem_modelos = [m["modelo"] for m in resumo["modelos"]]
    gbin = resumo["gabarito"]["composicao_binaria"]

    rotulos = ["Humano\n(gabarito)"] + ordem_modelos
    relevante = [gbin.get("relevante", 0)]
    naorel = [gbin.get("nao_relevante", 0)]
    erro = [0]
    for m in ordem_modelos:
        d = dist[m]
        relevante.append(d.get("super_relevante", 0) + d.get("relevante", 0))
        naorel.append(d.get("duvidoso", 0) + d.get("irrelevante", 0))
        erro.append(d.get("erro", 0))

    x = np.arange(len(rotulos))
    fig, ax = plt.subplots(figsize=(10, 5.8))
    segmentos = [
        (relevante, VERDE, "Relevante"),
        (naorel, CINZA, "Não-relevante"),
        (erro, VERMELHO, "Erro (formato)"),
    ]
    base = np.zeros(len(rotulos))
    # destaca a barra do humano com contorno
    bordas = ["#1d3557"] + ["white"] * len(ordem_modelos)
    larguras = [1.8] + [1.0] * len(ordem_modelos)
    for vals, cor, nome in segmentos:
        vals = np.array(vals, dtype=float)
        ax.bar(x, vals, bottom=base, color=cor, label=nome,
               edgecolor=bordas, linewidth=larguras, width=0.6)
        for i, v in enumerate(vals):
            if v >= 6:
                ax.text(i, base[i] + v / 2, int(v), ha="center", va="center",
                        fontsize=9, fontweight="bold", color="#1f2d3d")
        base += vals
    _so_grid_y(ax)
    ax.set_xticks(x, rotulos, fontsize=10)
    ax.set_ylabel("Número de documentos")
    _cabecalho(ax, "Relevância: humano vs. modelos",
               "Quantos documentos cada um considerou relevante (versão binária simplificada)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3,
              frameon=False, fontsize=9.5)
    salvar(fig, "01_comparativo_humano_modelos.png")


def g_gabarito(resumo: dict) -> None:
    """02 - Composição do gabarito humano (decisões originais)."""
    comp = resumo["gabarito"]["composicao_decisoes"]
    ordem = ["super_relevante", "aprovado", "ressalva", "rejeitado"]
    vals = [comp.get(k, 0) for k in ordem]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    b = ax.bar([ROTULO_HUMANO[k] for k in ordem], vals,
               color=[CORES_HUMANO[k] for k in ordem], width=0.62)
    ax.bar_label(b, fontsize=11, fontweight="bold", padding=3, color=TINTA)
    _so_grid_y(ax)
    ax.set_ylabel("Documentos")
    n = resumo["gabarito"]["n_docs"]
    _cabecalho(ax, "O gabarito humano",
               f"Decisões da validação manual ({n} documentos); relevante = super + aprovado + ressalva")
    salvar(fig, "02_gabarito_humano.png")


def g_pr_f1(resumo: dict) -> None:
    """03 - Precisão / Recall / F1."""
    mods = resumo["modelos"]
    modelos = [m["modelo"] for m in mods]
    rotulos = {"precisao": "Precisão", "recall": "Recall", "f1": "F1"}
    x = np.arange(len(modelos))
    w = 0.26
    fig, ax = plt.subplots(figsize=(10, 5.6))
    for i, chave in enumerate(["precisao", "recall", "f1"]):
        vals = [m[chave] for m in mods]
        barras = ax.bar(x + (i - 1) * w, vals, w, label=rotulos[chave],
                        color=PALETA_PRF[chave], edgecolor="white", linewidth=0.6)
        ax.bar_label(barras, fmt="%.2f", fontsize=8, padding=2, color="#33415c")
    _so_grid_y(ax)
    ax.set_xticks(x, modelos, fontsize=10)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Pontuação")
    _cabecalho(ax, "Precisão, Recall e F1 contra a validação humana",
               "Classe positiva = relevante  •  quanto mais alto, melhor")
    ax.legend(loc="upper right", frameon=False, fontsize=9.5, ncol=3)
    salvar(fig, "03_precisao_recall_f1.png")


def g_completude(resumo: dict) -> None:
    """04 - Quanto do corpus cada modelo conseguiu classificar."""
    dist = _dist_por_modelo(resumo)
    ordem = [m["modelo"] for m in resumo["modelos"]]
    corpus = resumo.get("corpus_n_docs", 203)
    validos, erros, faltando = [], [], []
    for m in ordem:
        d = dist[m]
        v = sum(d.get(c, 0) for c in
                ("super_relevante", "relevante", "duvidoso", "irrelevante"))
        e = d.get("erro", 0)
        validos.append(v)
        erros.append(e)
        faltando.append(max(0, corpus - v - e))

    x = np.arange(len(ordem))
    fig, ax = plt.subplots(figsize=(10, 5.4))
    base = np.zeros(len(ordem))
    for vals, cor, nome in [
        (validos, TEAL, "Classificados"),
        (erros, VERMELHO, "Falha de formato"),
        (faltando, CINZA_CLARO, "Não processados"),
    ]:
        vals = np.array(vals, dtype=float)
        ax.bar(x, vals, bottom=base, color=cor, label=nome, width=0.6,
               edgecolor="white", linewidth=1.0)
        for i, v in enumerate(vals):
            if v >= 5:
                ax.text(i, base[i] + v / 2, int(v), ha="center", va="center",
                        fontsize=9, fontweight="bold",
                        color="white" if cor == TEAL else "#1f2d3d")
        base += vals
    _so_grid_y(ax)
    ax.set_xticks(x, ordem, fontsize=10)
    ax.set_ylabel("Documentos")
    _cabecalho(ax, "Completude: quanto cada modelo classificou",
               f"De {corpus} documentos do corpus: classificados, falhas de formato e não processados")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=3,
              frameon=False, fontsize=9.5)
    salvar(fig, "04_completude.png")


def g_tempo(resumo: dict) -> None:
    """05 - Tempo mediano por documento."""
    mods = [m for m in resumo["modelos"] if m.get("tempo_mediano_doc_seg")]
    mods = sorted(mods, key=lambda m: m["tempo_mediano_doc_seg"])
    modelos = [m["modelo"] for m in mods]
    tempos = [m["tempo_mediano_doc_seg"] for m in mods]
    norm = Normalize(vmin=min(tempos), vmax=max(tempos))
    cores = matplotlib.colormaps["RdYlGn_r"](norm(tempos))
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    barras = ax.barh(modelos, tempos, color=cores, height=0.62,
                     edgecolor="white", linewidth=0.6)
    ax.bar_label(barras, labels=[f"{t:.0f}s" for t in tempos], fontsize=10,
                 padding=4, fontweight="bold", color="#33415c")
    _so_grid_x(ax)
    ax.set_xlabel("Segundos por documento (mediana)")
    ax.set_xlim(0, max(tempos) * 1.18)
    ax.invert_yaxis()
    _cabecalho(ax, "Tempo de processamento por documento",
               "Mediana fim-a-fim (inclui delimitador + download); não é inferência pura do classificador")
    salvar(fig, "05_tempo_por_modelo.png")


def g_matrizes(resumo: dict) -> None:
    """06 - Matrizes de confusão binárias."""
    matrizes = resumo["matrizes"]
    modelos = list(matrizes.keys())
    n = len(modelos)
    cols = 2
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4.6 * cols, 4.1 * rows))
    axes = np.array(axes).reshape(-1)
    labels = ["Não-rel.", "Relevante"]
    for ax, modelo in zip(axes, modelos):
        mb = matrizes[modelo]["binaria"]
        mat = np.array(mb["matriz"], dtype=float)
        im = ax.imshow(mat, cmap="Blues", aspect="equal")
        ax.set_xticks([0, 1], labels=labels, fontsize=9)
        ax.set_yticks([0, 1], labels=labels, fontsize=9, rotation=90, va="center")
        ax.set_xlabel("Predito pelo modelo", fontsize=9)
        ax.set_ylabel("Gabarito (humano)", fontsize=9)
        ax.set_title(f"{modelo}   ·   F1 = {mb['f1']:.2f}", fontsize=11,
                     fontweight="bold", color=TINTA, pad=8)
        thr = mat.max() / 2 if mat.max() else 0
        for i in range(2):
            linha = mat[i].sum()
            for j in range(2):
                cor = "white" if mat[i, j] > thr else "#1d3557"
                pct = 100 * mat[i, j] / linha if linha else 0
                ax.text(j, i - 0.08, f"{int(mat[i, j])}", ha="center", va="center",
                        color=cor, fontsize=15, fontweight="bold")
                ax.text(j, i + 0.22, f"{pct:.0f}%", ha="center", va="center",
                        color=cor, fontsize=8.5)
        ax.grid(False)
        for spine in ax.spines.values():
            spine.set_visible(False)
    for ax in axes[n:]:
        ax.axis("off")
    fig.suptitle("Matrizes de confusão (binário) vs. validação humana",
                 fontsize=15.5, fontweight="bold", color=TINTA, x=0.02, ha="left")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    salvar(fig, "06_matrizes_confusao.png")


def main() -> None:
    _tema()
    resumo = carregar()
    print("Gerando gráficos estilizados em docs/graficos/ ...")
    g_comparativo(resumo)
    g_gabarito(resumo)
    g_pr_f1(resumo)
    g_completude(resumo)
    g_tempo(resumo)
    g_matrizes(resumo)
    print("Concluído.")


if __name__ == "__main__":
    main()
