#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera as figuras do README (PNG, 150 dpi).

Dependência opcional: matplotlib (apenas para (re)gerar as imagens; os scripts
da skill usam somente a biblioteca padrão).

Uso:
  python3 scripts/gerar-figuras.py [pasta_de_saida]   # padrão: images/
"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

AZUL = "#1f5fbf"
AZUL_CLARO = "#eaf1fb"
AMARELO = "#fff3cd"
CINZA_CLARO = "#f2f2f2"


def box(ax, x, y, w, h, text, fc="white", ec=AZUL, fs=9.5, weight="normal"):
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.015",
        fc=fc, ec=ec, lw=1.4,
    )
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color="#111111", weight=weight, linespacing=1.35)


def arrow(ax, x1, y1, x2, y2):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                        color="#333333", lw=1.3)
    ax.add_patch(a)


def fig_workflow(out):
    """Fluxo de trabalho da skill: triagem + 10 fases."""
    fases = [
        ("Triagem", "nova ou atualização · do zero, em construção ou auditar"),
        ("Fase 1 · Título e introdução", "itens 1–4"),
        ("Fase 2 · Métodos: elegibilidade e fontes", "itens 5–6"),
        ("Fase 3 · Busca: estratégia e execução", "itens 6–7 · busca.py + manual.md"),
        ("Fase 4 · Seleção, coleta e dados", "itens 8–10b"),
        ("Fase 5 · Risco de viés, efeito e síntese", "itens 11–15"),
        ("Fase 6 · Resultados", "itens 16a–22"),
        ("Fase 7 · Discussão e outras informações", "itens 23a–27"),
        ("Fase 8 · Fluxograma PRISMA 2020", "fluxograma.py → PRISMA.csv → app Shiny"),
        ("Fase 9 · Resumos", "12 itens (Tabela 2)"),
        ("Fase 10 · Auditoria de conformidade", "27 itens: OK / PENDENTE / N.A."),
    ]
    fig, ax = plt.subplots(figsize=(9, 13))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 13.4)
    ax.axis("off")

    y = 12.4
    step = 1.12
    for i, (t, s) in enumerate(fases):
        fc = AZUL_CLARO if i % 2 == 0 else "white"
        box(ax, 1.2, y - 0.8, 7.6, 0.92, "%s\n%s" % (t, s), fc=fc, fs=10)
        if i < len(fases) - 1:
            arrow(ax, 5.0, y - 0.8, 5.0, y - step - 0.04)
        y -= step

    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_busca(out):
    """Módulo de busca: fontes abertas (script) vs. bloqueadas (manual)."""
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")

    box(ax, 0.3, 6.0, 3.4, 1.5,
        "PICO → estratégia (PT + EN)\nDeCS/MeSH · validada pelo usuário", fc=AMARELO)
    box(ax, 0.3, 2.3, 3.4, 2.6,
        "Fontes abertas (API, sem chave)\npubmed · europepmc\nopenalex · crossref\nsemanticscholar · doaj\nclinicaltrials")
    box(ax, 0.3, 0.3, 3.4, 1.5,
        "Fontes bloqueadas\nScopus · WoS · Embase\nLILACS/BVS · CENTRAL · ReBDc\nSciELO · Google Scholar", fc=CINZA_CLARO)

    box(ax, 5.1, 2.3, 3.0, 2.6, "scripts/busca.py\nregistros.csv\nresumo-busca.json")
    box(ax, 5.1, 0.3, 3.0, 1.5, "busca/manual.md\ndata + estratégia + contagem", fc=CINZA_CLARO)

    box(ax, 9.0, 2.6, 2.7, 2.0,
        "Fluxograma PRISMA 2020\nfluxograma.py →\nPRISMA.csv → app Shiny")

    arrow(ax, 2.0, 6.0, 2.0, 4.95)
    arrow(ax, 3.7, 3.6, 5.1, 3.6)
    arrow(ax, 3.7, 1.05, 5.1, 1.05)
    arrow(ax, 8.1, 3.6, 9.0, 3.9)
    arrow(ax, 8.1, 1.05, 9.3, 2.6)

    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "images"
    os.makedirs(out, exist_ok=True)
    fig_workflow(os.path.join(out, "workflow-skill.png"))
    fig_busca(os.path.join(out, "modulo-busca.png"))
    print("figuras geradas em", out)


if __name__ == "__main__":
    main()
