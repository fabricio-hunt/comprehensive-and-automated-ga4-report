"""
Geração de todos os gráficos do relatório SEO Bemol.
Salva cada gráfico como PNG temporário para uso no PDF.
Paleta de cores baseada no relatório original.
"""

import io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

# ── Paleta Bemol ──────────────────────────────────────────────────────────────
AZUL = "#1565C0"
AZUL_CLARO = "#42A5F5"
CINZA = "#64748B"
CINZA_ESCURO = "#757575"
VERDE = "#4CAF50"
VERMELHO = "#F44336"
ROXO = "#9C27B0"
VERDE_AGUA = "#00BCD4"
FUNDO = "#F5F5F5"
FUNDO_CARD = "#FFFFFF"

MESES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
            "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def _salvar_buffer(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=FUNDO_CARD)
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def _fmt_milhoes(v: float) -> str:
    if v >= 1_000_000:
        return f"R$ {v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"R$ {v/1_000:.0f}k"
    return f"R$ {v:.0f}"


def _fmt_num(v: float) -> str:
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v/1_000:.0f}k"
    return f"{v:.0f}"


# ── 1. Gráfico de barras: Evolução de Sessões (2026 vs 2025) ─────────────────

def grafico_sessoes_barras(serie_atual: dict, serie_anterior: dict,
                            mes_atual: int) -> bytes:
    """
    Barras agrupadas por mês, mostrando 2025 (cinza) vs 2026 (azul).
    Só barras de 2026 até o mês atual.
    """
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=FUNDO_CARD)
    ax.set_facecolor(FUNDO_CARD)

    x = np.arange(12)
    w = 0.4

    vals_ant = [serie_anterior.get(m, {}).get("sessoes", 0) for m in range(1, 13)]
    vals_at = [serie_atual.get(m, {}).get("sessoes", 0) if m <= mes_atual else 0
               for m in range(1, 13)]

    bars_ant = ax.bar(x - w/2, vals_ant, w, color=CINZA, label="2025", zorder=3)
    bars_at = ax.bar(x + w/2, vals_at, w, color=AZUL, label="2026", zorder=3)

    # Rótulos apenas nas barras do ano atual
    for i, (bar, v) in enumerate(zip(bars_at, vals_at)):
        if v > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(vals_ant)/50,
                    _fmt_num(v), ha="center", va="bottom", fontsize=7,
                    color=AZUL, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(MESES_PT, fontsize=9)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: f"{v/1000:.0f}k"))
    ax.tick_params(axis="y", labelsize=8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.yaxis.set_visible(True)
    ax.grid(axis="y", linestyle="--", alpha=0.4, zorder=0)
    ax.legend(fontsize=9, framealpha=0)

    fig.tight_layout()
    return _salvar_buffer(fig)


# ── 2. Gráfico de linhas: Evolução da Receita Orgânica (2026 vs 2025) ─────────

def grafico_receita_linhas(serie_atual: dict, serie_anterior: dict,
                            mes_atual: int) -> bytes:
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=FUNDO_CARD)
    ax.set_facecolor(FUNDO_CARD)

    meses = list(range(1, 13))
    vals_ant = [serie_anterior.get(m, {}).get("receita", None) for m in meses]
    vals_at = [serie_atual.get(m, {}).get("receita", None) if m <= mes_atual else None
               for m in meses]

    ax.plot(meses, vals_ant, color=CINZA, linewidth=2, marker="o",
            markersize=5, label="2025", linestyle="--")
    vals_at_clean = [v for v in vals_at if v is not None]
    meses_at_clean = [m for m, v in zip(meses, vals_at) if v is not None]
    ax.plot(meses_at_clean, vals_at_clean, color=AZUL, linewidth=2.5,
            marker="o", markersize=6, label="2026")

    ax.set_xticks(meses)
    ax.set_xticklabels(MESES_PT, fontsize=8)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: f"R$ {v/1_000_000:.1f}M"))
    ax.tick_params(axis="y", labelsize=8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(fontsize=9, framealpha=0)
    fig.tight_layout()
    return _salvar_buffer(fig)


# ── 3. Gráfico de rosca: Share orgânico na receita total ─────────────────────

def grafico_rosca_share(share_pct: float, label_organico: str = "Orgânico",
                         label_outros: str = "Outros canais") -> bytes:
    fig, ax = plt.subplots(figsize=(3.5, 3.5), facecolor=FUNDO_CARD)
    ax.set_facecolor(FUNDO_CARD)

    valores = [share_pct, 100 - share_pct]
    cores = [AZUL, CINZA]
    wedges, _ = ax.pie(valores, colors=cores, startangle=90,
                        wedgeprops=dict(width=0.45, edgecolor="white"))

    ax.text(0, 0, f"{share_pct:.1f}%", ha="center", va="center",
            fontsize=18, fontweight="bold", color=AZUL)
    ax.text(0, -0.22, "do site", ha="center", va="center",
            fontsize=9, color=CINZA_ESCURO)
    fig.tight_layout()
    return _salvar_buffer(fig)


# ── 4. Gráfico de barras: Receita por Sessão (Orgânico vs Total) ──────────────

def grafico_barra_receita_sessao(rps_organico: float, rps_total: float) -> bytes:
    fig, ax = plt.subplots(figsize=(3.5, 3.5), facecolor=FUNDO_CARD)
    ax.set_facecolor(FUNDO_CARD)

    categorias = ["Orgânico", "Total"]
    valores = [rps_organico, rps_total]
    cores = [AZUL, CINZA]

    bars = ax.bar(categorias, valores, color=cores, width=0.5, edgecolor="white")
    for bar, v in zip(bars, valores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f"R$ {v:.2f}", ha="center", va="bottom", fontsize=10,
                fontweight="bold", color=bar.get_facecolor())

    ax.set_ylabel("Receita por Sessão", fontsize=8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_ylim(0, max(valores) * 1.3)
    fig.tight_layout()
    return _salvar_buffer(fig)


# ── 5. Gráfico de linhas: Evolução Comparativa (índice base 100) ──────────────

def grafico_indice_comparativo(dados: dict, mes_atual: int) -> bytes:
    """
    dados = {
      'organico_ant': [...12 valores...],
      'total_ant': [...12 valores...],
      'organico_atual': [...12 valores...],
      'total_atual': [...12 valores...],
    }
    """
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=FUNDO_CARD)
    ax.set_facecolor(FUNDO_CARD)

    # Ano anterior + atual = 24 pontos
    org_ant = dados.get("organico_ant", [0]*12)
    tot_ant = dados.get("total_ant", [0]*12)
    org_at = dados.get("organico_atual", [0]*12)
    tot_at = dados.get("total_atual", [0]*12)

    base_org = org_ant[0] or 1
    base_tot = tot_ant[0] or 1

    idx_org = [v/base_org*100 for v in org_ant] + \
               [v/base_org*100 if i < mes_atual else None for i, v in enumerate(org_at, 1)]
    idx_tot = [v/base_tot*100 for v in tot_ant] + \
               [v/base_tot*100 if i < mes_atual else None for i, v in enumerate(tot_at, 1)]

    x = list(range(24))
    labels_x = [f"{m[:3]}/25" for m in MESES_PT] + [f"{m[:3]}/26" for m in MESES_PT]

    def plot_serie(vals, cor, estilo, rotulo):
        xs = [i for i, v in zip(x, vals) if v is not None]
        ys = [v for v in vals if v is not None]
        ax.plot(xs, ys, color=cor, linestyle=estilo, linewidth=2,
                marker="o", markersize=4, label=rotulo)

    plot_serie(idx_org, AZUL, "-", "Receita orgânica")
    plot_serie(idx_tot, CINZA, "--", "Receita total")

    ax.set_xticks(x[::2])
    ax.set_xticklabels(labels_x[::2], fontsize=7, rotation=30, ha="right")
    ax.set_ylabel("Índice (jan/25 = 100)", fontsize=8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.legend(fontsize=9, framealpha=0)
    fig.tight_layout()
    return _salvar_buffer(fig)


# ── 6. Gráfico de linhas: Evolução de Impressões GSC ─────────────────────────

def grafico_impressoes_linha(serie: dict) -> bytes:
    """serie = {'labels': [...], 'impressoes': [...]}"""
    fig, ax = plt.subplots(figsize=(7, 3.5), facecolor=FUNDO_CARD)
    ax.set_facecolor(FUNDO_CARD)

    labels = serie.get("labels", [])
    vals = serie.get("impressoes", [])

    ax.plot(range(len(vals)), vals, color=AZUL, linewidth=2.5,
            marker="o", markersize=6)
    ax.fill_between(range(len(vals)), vals, alpha=0.1, color=AZUL)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: f"{v/1_000_000:.1f}M" if v >= 1_000_000 else f"{v/1_000:.0f}k"))
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.tick_params(axis="both", labelsize=8)
    fig.tight_layout()
    return _salvar_buffer(fig)


# ── 7. Gauge: Score de Visibilidade na IA ─────────────────────────────────────

def grafico_gauge_ia(score: float, label: str = "Média") -> bytes:
    """Gauge semicircular com score /100."""
    fig, ax = plt.subplots(figsize=(3.5, 2.2), facecolor=FUNDO_CARD,
                            subplot_kw=dict(polar=False))
    ax.set_facecolor(FUNDO_CARD)
    ax.set_aspect("equal")
    ax.axis("off")

    # Fundo do arco
    theta = np.linspace(np.pi, 0, 100)
    r = 1.0
    thick = 0.25

    def arco(t_start, t_end, cor, alpha=1.0):
        thetas = np.linspace(t_start, t_end, 50)
        xs_out = r * np.cos(thetas)
        ys_out = r * np.sin(thetas)
        xs_in = (r - thick) * np.cos(thetas[::-1])
        ys_in = (r - thick) * np.sin(thetas[::-1])
        ax.fill(np.concatenate([xs_out, xs_in]),
                np.concatenate([ys_out, ys_in]),
                color=cor, alpha=alpha)

    # Fundo cinza
    arco(np.pi, 0, CINZA, alpha=0.3)

    # Score colorido
    score_clamped = max(0, min(100, score))
    angle = np.pi - (score_clamped / 100) * np.pi

    if score_clamped < 33:
        cor_score = VERMELHO
    elif score_clamped < 66:
        cor_score = "#FF9800"
    else:
        cor_score = VERDE

    arco(np.pi, angle, cor_score)

    # Ponteiro
    px = (r - thick/2) * np.cos(angle)
    py = (r - thick/2) * np.sin(angle)
    ax.annotate("", xy=(px, py), xytext=(0.55*np.cos(angle), 0.55*np.sin(angle)),
                arrowprops=dict(arrowstyle="-|>", color=AZUL_ESCURO if score > 50 else CINZA_ESCURO,
                                lw=2))

    ax.text(0, 0.15, f"{int(score_clamped)}", ha="center", va="center",
            fontsize=20, fontweight="bold", color=cor_score)
    ax.text(0, -0.08, "/100", ha="center", va="center",
            fontsize=10, color=CINZA_ESCURO)
    ax.text(0, -0.28, label, ha="center", va="center",
            fontsize=11, fontweight="bold", color=CINZA_ESCURO)

    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.5, 1.2)
    fig.tight_layout()
    return _salvar_buffer(fig)


AZUL_ESCURO = "#0D47A1"


# ── 8. Gráfico de linhas: Série histórica de IA ───────────────────────────────

def grafico_serie_ia(serie: dict) -> bytes:
    """Três linhas: menções, citações, páginas citadas."""
    fig, ax = plt.subplots(figsize=(6.5, 3.5), facecolor=FUNDO_CARD)
    ax.set_facecolor(FUNDO_CARD)

    labels = serie.get("labels", [])
    n = len(labels)
    if n == 0:
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center",
                transform=ax.transAxes, fontsize=12, color=CINZA_ESCURO)
        return _salvar_buffer(fig)

    x = range(n)
    ax.plot(x, serie["mencoes"], color=ROXO, marker="o", linewidth=2,
            markersize=5, label="Menções")
    ax.plot(x, serie["citacoes"], color=VERDE_AGUA, marker="o", linewidth=2,
            markersize=5, label="Citações")
    ax.plot(x, serie["paginas_citadas"], color=AZUL_CLARO, marker="o",
            linewidth=2, markersize=5, label="Páginas citadas")

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=8, rotation=20, ha="right")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: f"{v/1000:.0f} mil" if v >= 1000 else str(int(v))))
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(fontsize=8, framealpha=0)
    ax.tick_params(axis="both", labelsize=8)
    fig.tight_layout()
    return _salvar_buffer(fig)


# ── 9. Gráfico de linhas: Receita Orgânica App (2026 vs 2025) ─────────────────

def grafico_receita_app(serie_atual: dict, serie_anterior: dict,
                         mes_atual: int) -> bytes:
    return grafico_receita_linhas(serie_atual, serie_anterior, mes_atual)
