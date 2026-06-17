"""Gera os gráficos a partir de docs/dados/ (saída do gerar_metricas.py).

Lê docs/dados/resumo.json e escreve PNGs estilizados em docs/graficos/.
Não acessa o banco. O gabarito é a validação humana (tabela Review).

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
TINTA = "#1d3557"      # titulos
TINTA2 = "#6c757d"     # subtitulos
GRID = "#e9ecef"

PALETA_PRF = {"precisao": "#89c2d9", "recall": "#468faf", "f1": "#013a63"}
CORES_CLASSE = {
    "super_relevante": "#1b7837",
    "relevante": "#8cce8a",
    "duvidoso": "#f4a259",
    "irrelevante": "#ced4da",
    "erro": "#bc4749",
}
ROTULO_CLASSE = {
    "super_relevante": "Super relevante", "relevante": "Relevante",
    "duvidoso": "Duvidoso", "irrelevante": "Irrelevante", "erro": "Erro (formato)",
}
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
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.edgecolor": "#ced4da",
        "axes.linewidth": 1.0,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 1.0,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "xtick.color": "#495057",
        "ytick.color": "#495057",
        "axes.labelcolor": "#495057",
        "figure.dpi": 160,
    })


def _cabecalho(ax, titulo: str, subtitulo: str = "") -> None:
    ax.text(0.0, 1.16, titulo, transform=ax.transAxes, fontsize=15.5,
            fontweight="bold", color=TINTA, va="top")
    if subtitulo:
        ax.text(0.0, 1.075, subtitulo, transform=ax.transAxes, fontsize=9.5,
                color=TINTA2, va="top")


def carregar() -> dict:
    with open(DADOS_DIR / "resumo.json", encoding="utf-8") as fh:
        return json.load(fh)


def salvar(fig, nome: str) -> None:
    fig.savefig(GRAF_DIR / nome, dpi=160, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print(f"  -> {nome}")


def _so_grid_y(ax) -> None:
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", visible=True)


def _so_grid_x(ax) -> None:
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)


# ---------------------------------------------------------------------------
def g_distribuicao(resumo: dict) -> None:
    dist = resumo["distribuicao"]
    modelos = [d["modelo"] for d in dist]
    classes = ["super_relevante", "relevante", "duvidoso", "irrelevante", "erro"]
    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    base = np.zeros(len(modelos))
    for c in classes:
        vals = np.array([d.get(c, 0) for d in dist], dtype=float)
        ax.bar(modelos, vals, bottom=base, label=ROTULO_CLASSE[c],
               color=CORES_CLASSE[c], edgecolor="white", linewidth=1.2, width=0.62)
        for i, v in enumerate(vals):
            if v >= 8:
                ax.text(i, base[i] + v / 2, int(v), ha="center", va="center",
                        fontsize=8.5, color="#1f2d3d", fontweight="bold")
        base += vals
    _so_grid_y(ax)
    ax.set_ylabel("Número de documentos")
    ax.set_axisbelow(True)
    _cabecalho(ax, "Como cada modelo distribui seus rótulos",
               "Composição das classes atribuídas por modelo (corpus: 203 documentos)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=5,
              frameon=False, fontsize=8.8, handlelength=1.2)
    ax.tick_params(axis="x", labelsize=10)
    salvar(fig, "01_distribuicao_classes.png")


def g_gabarito(resumo: dict) -> None:
    comp = resumo["gabarito"]["composicao_decisoes"]
    binr = resumo["gabarito"]["composicao_binaria"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6),
                                   gridspec_kw={"wspace": 0.25})
    ordem = ["super_relevante", "aprovado", "ressalva", "rejeitado"]
    vals = [comp.get(k, 0) for k in ordem]
    b = ax1.bar([ROTULO_HUMANO[k] for k in ordem], vals,
                color=[CORES_HUMANO[k] for k in ordem], width=0.66)
    ax1.bar_label(b, fontsize=10, fontweight="bold", padding=2, color=TINTA)
    _so_grid_y(ax1)
    ax1.set_ylabel("Documentos")
    ax1.set_title("Decisões originais", fontsize=11, color=TINTA2, pad=6)
    ax1.tick_params(axis="x", labelsize=9.5)

    bvals = [binr.get("relevante", 0), binr.get("nao_relevante", 0)]
    b2 = ax2.bar(["Relevante", "Não-relevante"], bvals,
                 color=["#8cce8a", "#ced4da"], width=0.55)
    ax2.bar_label(b2, fontsize=11, fontweight="bold", padding=2, color=TINTA)
    _so_grid_y(ax2)
    ax2.set_title("Agrupado em binário", fontsize=11, color=TINTA2, pad=6)

    fig.text(0.0, 1.02, "O gabarito humano", fontsize=15.5, fontweight="bold",
             color=TINTA, va="bottom", transform=ax1.transAxes)
    fig.text(0.0, 0.965, "Validação manual de 202 documentos (tabela Review)",
             fontsize=9.5, color=TINTA2, va="bottom", transform=ax1.transAxes)
    salvar(fig, "02_gabarito_humano.png")


def g_pr_f1(resumo: dict) -> None:
    mods = resumo["modelos"]
    modelos = [m["modelo"] for m in mods]
    x = np.arange(len(modelos))
    w = 0.26
    rotulos = {"precisao": "Precisão", "recall": "Recall", "f1": "F1"}
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


def g_acuracia_cobertura(resumo: dict) -> None:
    mods = resumo["modelos"]
    modelos = [m["modelo"] for m in mods]
    acc = [m["acuracia"] for m in mods]
    cob = [m["cobertura"] for m in mods]
    x = np.arange(len(modelos))
    w = 0.38
    fig, ax = plt.subplots(figsize=(10, 5.6))
    b1 = ax.bar(x - w / 2, acc, w, label="Acurácia (binária)", color="#2c7da0",
                edgecolor="white", linewidth=0.6)
    b2 = ax.bar(x + w / 2, cob, w, label="Cobertura do gabarito", color="#a8dadc",
                edgecolor="white", linewidth=0.6)
    ax.bar_label(b1, fmt="%.2f", fontsize=8, padding=2, color="#33415c")
    ax.bar_label(b2, fmt="%.2f", fontsize=8, padding=2, color="#33415c")
    aux = resumo.get("referencia_auxiliar", {}).get("concordancia")
    if aux is not None:
        ax.axhline(aux, ls=(0, (5, 4)), color="#adb5bd", lw=1.3)
        ax.text(len(modelos) - 0.5, aux + 0.015,
                f"modelo-assistente × humano = {aux*100:.0f}%",
                color="#868e96", ha="right", fontsize=8.5, style="italic")
    _so_grid_y(ax)
    ax.set_xticks(x, modelos, fontsize=10)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Proporção")
    _cabecalho(ax, "Acurácia e cobertura por modelo",
               "Acurácia = acerto vs. humano  •  Cobertura = fração do corpus que o modelo classificou")
    ax.legend(loc="upper right", frameon=False, fontsize=9.5)
    salvar(fig, "04_acuracia_cobertura.png")


def g_taxa_erro(resumo: dict) -> None:
    mods = sorted(resumo["modelos"], key=lambda m: m["taxa_erro"])
    modelos = [m["modelo"] for m in mods]
    erro = [m["taxa_erro"] * 100 for m in mods]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    barras = ax.barh(modelos, erro, color="#bc4749", height=0.6)
    ax.bar_label(barras, fmt="%.1f%%", fontsize=10, padding=4,
                 fontweight="bold", color="#7a2e30")
    _so_grid_x(ax)
    ax.set_xlabel("Falhas de formato (%)")
    ax.set_xlim(0, max(erro) * 1.25 if erro else 1)
    ax.invert_yaxis()
    _cabecalho(ax, "Confiabilidade de formato",
               "Respostas que não vieram no JSON esperado (menor é melhor)")
    salvar(fig, "05_taxa_erro.png")


def g_tempo(resumo: dict) -> None:
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
    salvar(fig, "06_tempo_por_modelo.png")


def g_matrizes(resumo: dict) -> None:
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
        total = mat.sum()
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
    salvar(fig, "07_matrizes_confusao.png")


def main() -> None:
    _tema()
    resumo = carregar()
    print("Gerando gráficos estilizados em docs/graficos/ ...")
    g_distribuicao(resumo)
    g_gabarito(resumo)
    g_pr_f1(resumo)
    g_acuracia_cobertura(resumo)
    g_taxa_erro(resumo)
    g_tempo(resumo)
    g_matrizes(resumo)
    print("Concluído.")


if __name__ == "__main__":
    main()
