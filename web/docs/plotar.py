"""Gera os graficos a partir de docs/dados/ (saida do gerar_metricas.py).

Le docs/dados/resumo.json e escreve PNGs em docs/graficos/.
Nao acessa o banco. O gabarito e a validacao humana (tabela Review).

Uso:
    python docs/plotar.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

DOCS_DIR = Path(__file__).resolve().parent
DADOS_DIR = DOCS_DIR / "dados"
GRAF_DIR = DOCS_DIR / "graficos"
GRAF_DIR.mkdir(exist_ok=True)

CORES = {
    "super_relevante": "#1b7837",
    "relevante": "#7fbf7b",
    "duvidoso": "#f1a340",
    "irrelevante": "#d9d9d9",
    "erro": "#b2182b",
}
ROTULO_CLASSE = {
    "super_relevante": "Super relevante",
    "relevante": "Relevante",
    "duvidoso": "Duvidoso",
    "irrelevante": "Irrelevante",
    "erro": "Erro (formato)",
}
# decisoes humanas (esquema da tabela Review)
CORES_HUMANO = {
    "super_relevante": "#1b7837",
    "aprovado": "#7fbf7b",
    "ressalva": "#f1a340",
    "rejeitado": "#b2182b",
}
ROTULO_HUMANO = {
    "super_relevante": "Super relevante",
    "aprovado": "Aprovado",
    "ressalva": "Ressalva",
    "rejeitado": "Rejeitado",
}


def carregar() -> dict:
    with open(DADOS_DIR / "resumo.json", encoding="utf-8") as fh:
        return json.load(fh)


def salvar(fig, nome: str) -> None:
    fig.savefig(GRAF_DIR / nome, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {nome}")


# ---------------------------------------------------------------------------
def g_distribuicao(resumo: dict) -> None:
    """Barras empilhadas: como cada modelo distribui seus rotulos."""
    dist = resumo["distribuicao"]
    modelos = [d["modelo"] for d in dist]
    classes = ["super_relevante", "relevante", "duvidoso", "irrelevante", "erro"]
    fig, ax = plt.subplots(figsize=(9, 5))
    base = np.zeros(len(modelos))
    for c in classes:
        vals = np.array([d.get(c, 0) for d in dist], dtype=float)
        ax.bar(modelos, vals, bottom=base, label=ROTULO_CLASSE[c], color=CORES[c],
               edgecolor="white", linewidth=0.5)
        base += vals
    ax.set_ylabel("Numero de documentos")
    ax.set_title("Distribuicao dos rotulos por modelo")
    ax.legend(loc="upper right", fontsize=8, framealpha=0.9)
    ax.tick_params(axis="x", rotation=15)
    salvar(fig, "01_distribuicao_classes.png")


def g_gabarito(resumo: dict) -> None:
    """Composicao do gabarito humano: decisoes originais + split binario."""
    comp = resumo["gabarito"]["composicao_decisoes"]
    binr = resumo["gabarito"]["composicao_binaria"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))

    ordem = ["super_relevante", "aprovado", "ressalva", "rejeitado"]
    labels = [ROTULO_HUMANO[k] for k in ordem]
    vals = [comp.get(k, 0) for k in ordem]
    cores = [CORES_HUMANO[k] for k in ordem]
    b = ax1.bar(labels, vals, color=cores)
    ax1.bar_label(b, fontsize=9)
    ax1.set_title("Gabarito humano - decisoes")
    ax1.set_ylabel("Documentos")
    ax1.tick_params(axis="x", rotation=15)

    bvals = [binr.get("relevante", 0), binr.get("nao_relevante", 0)]
    b2 = ax2.bar(["Relevante", "Nao-relevante"], bvals, color=["#7fbf7b", "#d9d9d9"])
    ax2.bar_label(b2, fontsize=10)
    ax2.set_title("Gabarito humano - binario")
    fig.tight_layout()
    salvar(fig, "02_gabarito_humano.png")


def g_pr_f1(resumo: dict) -> None:
    modelos = [m["modelo"] for m in resumo["modelos"]]
    prec = [m["precisao"] for m in resumo["modelos"]]
    rec = [m["recall"] for m in resumo["modelos"]]
    f1 = [m["f1"] for m in resumo["modelos"]]
    x = np.arange(len(modelos))
    w = 0.26
    fig, ax = plt.subplots(figsize=(9, 5))
    for i, (vals, nome, cor) in enumerate([
        (prec, "Precisao", "#4575b4"),
        (rec, "Recall", "#91bfdb"),
        (f1, "F1", "#313695"),
    ]):
        barras = ax.bar(x + (i - 1) * w, vals, w, label=nome, color=cor)
        ax.bar_label(barras, fmt="%.2f", fontsize=7, padding=2)
    ax.set_xticks(x)
    ax.set_xticklabels(modelos, rotation=15)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Pontuacao")
    ax.set_title("Precisao / Recall / F1 vs. validacao humana (positivo = relevante)")
    ax.legend(fontsize=8)
    salvar(fig, "03_precisao_recall_f1.png")


def g_acuracia_cobertura(resumo: dict) -> None:
    modelos = [m["modelo"] for m in resumo["modelos"]]
    acc = [m["acuracia"] for m in resumo["modelos"]]
    cob = [m["cobertura"] for m in resumo["modelos"]]
    x = np.arange(len(modelos))
    w = 0.38
    fig, ax = plt.subplots(figsize=(9, 5))
    b1 = ax.bar(x - w / 2, acc, w, label="Acuracia (binaria)", color="#2c7fb8")
    b2 = ax.bar(x + w / 2, cob, w, label="Cobertura do gabarito", color="#a1dab4")
    ax.bar_label(b1, fmt="%.2f", fontsize=7)
    ax.bar_label(b2, fmt="%.2f", fontsize=7)

    aux = resumo.get("referencia_auxiliar", {}).get("concordancia")
    if aux is not None:
        ax.axhline(aux, ls="--", color="#777777", lw=1.1)
        ax.text(len(modelos) - 0.5, aux + 0.01,
                f"modelo-assistente x humano = {aux*100:.0f}%",
                color="#555555", ha="right", fontsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels(modelos, rotation=15)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Proporcao")
    ax.set_title("Acuracia e cobertura por modelo (vs. humano)")
    ax.legend(fontsize=8, loc="lower right")
    salvar(fig, "04_acuracia_cobertura.png")


def g_taxa_erro(resumo: dict) -> None:
    modelos = [m["modelo"] for m in resumo["modelos"]]
    erro = [m["taxa_erro"] * 100 for m in resumo["modelos"]]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    barras = ax.bar(modelos, erro, color="#d6604d")
    ax.bar_label(barras, fmt="%.1f%%", fontsize=8)
    ax.set_ylabel("Falhas de formato (%)")
    ax.set_title("Taxa de erro de formato por modelo")
    ax.tick_params(axis="x", rotation=15)
    salvar(fig, "05_taxa_erro.png")


def g_matrizes(resumo: dict) -> None:
    matrizes = resumo["matrizes"]
    modelos = list(matrizes.keys())
    n = len(modelos)
    cols = 2
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4.2 * cols, 3.8 * rows))
    axes = np.array(axes).reshape(-1)
    labels = ["nao_rel.", "relevante"]
    for ax, modelo in zip(axes, modelos):
        mb = matrizes[modelo]["binaria"]
        mat = np.array(mb["matriz"])
        im = ax.imshow(mat, cmap="Blues")
        ax.set_xticks([0, 1], labels=labels)
        ax.set_yticks([0, 1], labels=labels)
        ax.set_xlabel("Predito (modelo)")
        ax.set_ylabel("Gabarito (humano)")
        ax.set_title(f"{modelo} (F1={mb['f1']:.2f})", fontsize=10)
        thr = mat.max() / 2 if mat.max() else 0
        for i in range(2):
            for j in range(2):
                ax.text(j, i, int(mat[i, j]), ha="center", va="center",
                        color="white" if mat[i, j] > thr else "black", fontsize=11)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    for ax in axes[n:]:
        ax.axis("off")
    fig.suptitle("Matrizes de confusao (binario) vs. validacao humana", y=1.0)
    fig.tight_layout()
    salvar(fig, "06_matrizes_confusao.png")


def main() -> None:
    resumo = carregar()
    print("Gerando graficos em docs/graficos/ ...")
    g_distribuicao(resumo)
    g_gabarito(resumo)
    g_pr_f1(resumo)
    g_acuracia_cobertura(resumo)
    g_taxa_erro(resumo)
    g_matrizes(resumo)
    print("Concluido.")


if __name__ == "__main__":
    main()
