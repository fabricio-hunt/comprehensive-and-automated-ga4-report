"""
Monta o PDF do Relatório SEO Bemol com ReportLab.
Formato: A4 landscape (297 x 210 mm) — mesmo do relatório original.
Cada função gera um slide/página.
"""

import io
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from unidecode import unidecode

def _s(text: str) -> str:
    """Remove acentos para compatibilidade com fontes padrao do PDF."""
    if isinstance(text, str):
        return unidecode(text)
    return str(text)

# ── Dimensões ─────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = landscape(A4)   # 841.89 x 595.28 pts

# ── Cores ─────────────────────────────────────────────────────────────────────
AZUL = colors.HexColor("#1565C0")
AZUL_CLARO = colors.HexColor("#42A5F5")
CINZA_BG = colors.HexColor("#F5F5F5")
CINZA_TEXTO = colors.HexColor("#757575")
BRANCO = colors.white
VERDE = colors.HexColor("#4CAF50")
VERMELHO = colors.HexColor("#F44336")
AZUL_CARD_BG = colors.HexColor("#E3F2FD")

MESES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
            "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _img(png_bytes: bytes):
    return ImageReader(io.BytesIO(png_bytes))


def _fmt_brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_num(v: float) -> str:
    return f"{v:,.0f}".replace(",", ".")


def _cor_var(v) -> colors.Color:
    if v is None:
        return CINZA_TEXTO
    try:
        return VERDE if float(v) >= 0 else VERMELHO
    except (TypeError, ValueError):
        return CINZA_TEXTO


def _seta(v) -> str:
    if v is None:
        return "-"
    try:
        val = float(v)
    except (TypeError, ValueError):
        return "-"
    return ("+" if val >= 0 else "-") + f" {abs(val):.1f}%"


def _seta_pp(v) -> str:
    if v is None:
        return "-"
    try:
        val = float(v)
    except (TypeError, ValueError):
        return "-"
    return ("+" if val >= 0 else "-") + f" {abs(val):.1f} p.p."


def _fundo_pagina(c: canvas.Canvas, titulo: str = "",
                   logo_path: str = None, logo_w: float = 80, cor_linha: bool = True):
    """Fundo padrão: bg cinza claro + linha azul no topo + título + logo."""
    c.setFillColor(CINZA_BG)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    if cor_linha:
        c.setFillColor(AZUL)
        c.rect(0, PAGE_H - 4, PAGE_W, 4, fill=1, stroke=0)

    if titulo:
        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(AZUL)
        c.drawString(30*mm, PAGE_H - 22*mm, titulo)

    if logo_path and Path(logo_path).exists():
        try:
            c.drawImage(logo_path, PAGE_W - logo_w - 15*mm,
                        PAGE_H - 18*mm, width=logo_w, height=16*mm,
                        preserveAspectRatio=True, mask="auto")
        except Exception:
            pass


def _card_kpi(c: canvas.Canvas, x, y, w, h,
              titulo: str, valor: str,
              label_yoy: str, var_yoy, valor_yoy: str,
              label_mom: str, var_mom, valor_mom: str,
              unidade: str = "", pp: bool = False):
    """
    Desenha um card de KPI com valor principal + comparacoes YoY e MoM.
    """
    titulo_s = _s(titulo)
    valor_s = _s(valor)
    label_yoy_s = _s(label_yoy)
    valor_yoy_s = _s(valor_yoy)
    label_mom_s = _s(label_mom)
    valor_mom_s = _s(valor_mom)
    unidade_s = _s(unidade)

    # fundo branco arredondado (simulado com rect)
    c.setFillColor(BRANCO)
    c.roundRect(x, y, w, h, 6, fill=1, stroke=0)

    # Titulo
    c.setFont("Helvetica", 8)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(x + 8, y + h - 16, titulo_s.upper())

    # Valor principal
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.HexColor("#212121"))
    c.drawString(x + 8, y + h - 36, valor_s + unidade_s)

    # YoY
    c.setFont("Helvetica", 7.5)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(x + 8, y + h - 52, label_yoy_s)
    c.drawString(x + 8, y + h - 62, valor_yoy_s)

    # Badge YoY
    cor = _cor_var(var_yoy)
    _badge_variacao(c, x + w - 52, y + h - 65,
                    _seta_pp(var_yoy) if pp else _seta(var_yoy), cor)

    # MoM
    c.setFont("Helvetica", 7.5)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(x + 8, y + 28, label_mom_s)
    c.drawString(x + 8, y + 18, valor_mom_s)

    # Badge MoM
    cor_m = _cor_var(var_mom)
    _badge_variacao(c, x + w - 52, y + 15,
                    _seta_pp(var_mom) if pp else _seta(var_mom), cor_m)


def _badge_variacao(c: canvas.Canvas, x, y, texto: str, cor: colors.Color):
    """Pequeno badge colorido com variação percentual."""
    w, h = 46, 13
    c.setFillColor(cor.clone() if hasattr(cor, "clone") else cor)
    # fundo levemente transparente
    r, g, b = cor.red, cor.green, cor.blue
    c.setFillColorRGB(r, g, b, alpha=0.15)
    c.roundRect(x, y, w, h, 4, fill=1, stroke=0)
    c.setFillColor(cor)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(x + w/2, y + 3, texto)


def _caixa_texto(c: canvas.Canvas, x, y, w, h, texto: str,
                  bg=AZUL_CARD_BG, font_size=8.5):
    """Caixa de texto azul claro com texto explicativo."""
    c.setFillColor(bg)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#0D47A1"))
    c.setFont("Helvetica", font_size)
    _draw_wrapped_text(c, texto, x + 10, y + h - 14, w - 20, font_size, line_height=13)


def _draw_wrapped_text(c: canvas.Canvas, text: str, x, y, max_w, font_size, line_height=13):
    """Quebra texto em linhas para caber na largura."""
    words = text.split()
    line = ""
    cy = y
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, "Helvetica", font_size) <= max_w:
            line = test
        else:
            if line:
                c.drawString(x, cy, line)
                cy -= line_height
            line = word
    if line:
        c.drawString(x, cy, line)


# ── Slides ────────────────────────────────────────────────────────────────────

def slide_capa(c: canvas.Canvas, mes_nome: str, ano: int,
               logo_bemol: str, logo_farma: str):
    """Slide 1: Capa."""
    c.setFillColor(CINZA_BG)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Linha decorativa
    c.setFillColor(AZUL)
    c.rect(30*mm, 35*mm, 60*mm, 2, fill=1, stroke=0)

    # Título
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(AZUL)
    c.drawString(30*mm, PAGE_H/2 + 30, "Relatório SEO & Search")

    # Subtítulo
    c.setFont("Helvetica", 22)
    c.setFillColor(AZUL_CLARO)
    c.drawString(30*mm, PAGE_H/2, f"{mes_nome} / {ano}")

    # Sub-subtítulo
    c.setFont("Helvetica", 12)
    c.setFillColor(AZUL_CLARO)
    c.drawString(30*mm, PAGE_H/2 - 22, "Bemol Varejo  ·  Bemol Farma  ·  App Bemol")

    # Logos
    logos = [logo_bemol, logo_farma]
    lx = 30*mm
    for lp in logos:
        if lp and Path(lp).exists():
            try:
                c.drawImage(lp, lx, 28*mm, width=70, height=25,
                            preserveAspectRatio=True, mask="auto")
                lx += 85
            except Exception:
                pass

    c.showPage()


def slide_visao_geral(c: canvas.Canvas, destaques: list[str], resumo: str):
    """Slide 2: Visão Geral."""
    _fundo_pagina(c, "Visao Geral", logo_path=None)

    # Resumo em negrito
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#212121"))
    _draw_wrapped_text(c, resumo, 30*mm, PAGE_H - 50*mm, PAGE_W - 60*mm, 10, 14)

    # Card de destaques
    cx, cy = 30*mm, 50*mm
    cw, ch = PAGE_W * 0.55, PAGE_H * 0.45
    c.setFillColor(AZUL_CARD_BG)
    c.roundRect(cx, cy, cw, ch, 10, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#0D47A1"))
    c.drawString(cx + 10, cy + ch - 18, "Destaques:")

    c.setFont("Helvetica", 9)
    ty = cy + ch - 34
    for destaque in destaques:
        _draw_wrapped_text(c, f"• {destaque}", cx + 10, ty, cw - 20, 9, 12)
        ty -= 38

    c.showPage()


def slide_performance_web_kpis(c: canvas.Canvas, kpis: dict, mes_nome: str, ano: int,
                                 logo_path: str):
    """Slide 3: Performance Orgânica → Web (KPIs)."""
    _fundo_pagina(c, "Performance Organica -> Web", logo_path)

    c.setFont("Helvetica", 9)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(30*mm, PAGE_H - 30*mm, f"mai/{str(ano)[2:]} vs mai/{str(ano-1)[2:]}  ·  vs abr/{str(ano)[2:]}")

    # 4 cards
    card_w = (PAGE_W - 70*mm) / 2
    card_h = 90
    gap = 8
    row1_y = PAGE_H - 145
    row2_y = PAGE_H - 145 - card_h - gap
    col1_x = 30*mm
    col2_x = 30*mm + card_w + gap

    atual = kpis["atual"]
    mom = kpis["mom"]
    yoy = kpis["yoy"]

    _card_kpi(c, col1_x, row1_y, card_w, card_h,
              "Sessões Orgânicas",
              _fmt_num(atual["sessoes"]), "",
              f"YOY · VS MAI/{ano-1}", kpis["var_yoy_sessoes"], _fmt_num(yoy["sessoes"]),
              f"MOM · VS ABR/{ano}", kpis["var_mom_sessoes"], _fmt_num(mom["sessoes"]))

    _card_kpi(c, col2_x, row1_y, card_w, card_h,
              "Taxa de Engajamento",
              f"{atual['tx_engajamento']:.2f}", "%",
              f"YOY · VS MAI/{ano-1}", kpis["var_yoy_tx_eng"],
              f"{yoy['tx_engajamento']:.2f}%",
              f"MOM · VS ABR/{ano}", kpis["var_mom_tx_eng"],
              f"{mom['tx_engajamento']:.2f}%", pp=True)

    _card_kpi(c, col1_x, row2_y, card_w, card_h,
              "Receita Orgânica",
              _fmt_brl(atual["receita"]), "",
              f"YOY · VS MAI/{ano-1}", kpis["var_yoy_receita"], _fmt_brl(yoy["receita"]),
              f"MOM · VS ABR/{ano}", kpis["var_mom_receita"], _fmt_brl(mom["receita"]))

    _card_kpi(c, col2_x, row2_y, card_w, card_h,
              "Total Usuários Orgânicos",
              _fmt_num(atual["usuarios"]), "",
              f"YOY · VS MAI/{ano-1}", kpis["var_yoy_usuarios"], _fmt_num(yoy["usuarios"]),
              f"MOM · VS ABR/{ano}", kpis["var_mom_usuarios"], _fmt_num(mom["usuarios"]))

    # Caixa texto
    txt = (f"Maio registrou recuperação da performance orgânica do Varejo. "
           f"Receita orgânica de {_fmt_brl(atual['receita'])}, "
           f"com crescimento de {abs(kpis['var_mom_receita'] or 0):.1f}% em relação a abril. "
           f"Sessões cresceram {abs(kpis['var_mom_sessoes'] or 0):.1f}% no mês.")
    _caixa_texto(c, 30*mm, 15*mm, PAGE_W - 60*mm, 45, txt)
    c.showPage()


def slide_performance_web_graficos(c: canvas.Canvas, img_sessoes: bytes,
                                    img_receita: bytes, kpis: dict,
                                    mes_nome: str, ano: int, logo_path: str):
    """Slide 4: Performance Orgânica → Web (gráficos)."""
    _fundo_pagina(c, "Performance Organica -> Web", logo_path)

    mid = PAGE_W / 2
    top_y = PAGE_H - 35*mm
    graf_h = 130

    # Gráfico sessões (esquerda)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#212121"))
    c.drawString(30*mm, top_y + 5, "Evolucao de Sessoes")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(30*mm, top_y - 8, f"2026 vs {ano-1}")
    c.drawImage(_img(img_sessoes), 25*mm, top_y - graf_h - 10,
                width=mid - 35*mm, height=graf_h)

    # Gráfico receita (direita)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#212121"))
    c.drawString(mid + 5*mm, top_y + 5, "Evolucao da Receita Organica")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(mid + 5*mm, top_y - 8, f"2026 vs {ano-1}")
    c.drawImage(_img(img_receita), mid, top_y - graf_h - 10,
                width=mid - 35*mm, height=graf_h)

    # Caixas texto
    atual = kpis["atual"]
    txt_l = (f"Sessões: {_fmt_num(atual['sessoes'])}, crescimento de "
             f"{abs(kpis['var_mom_sessoes'] or 0):.1f}% em relação a abril. "
             "O canal manteve sua capacidade de atrair usuários qualificados.")
    txt_r = (f"Receita orgânica de {_fmt_brl(atual['receita'])} em {mes_nome}, "
             f"resultado {abs(kpis['var_yoy_receita'] or 0):.1f}% superior ao mesmo mês do ano anterior.")

    _caixa_texto(c, 25*mm, 12*mm, mid - 35*mm, 50, txt_l)
    _caixa_texto(c, mid, 12*mm, mid - 35*mm, 50, txt_r)
    c.showPage()


def slide_organico_vs_total(c: canvas.Canvas, share_pct: float,
                             receita_organica: float, receita_total: float,
                             rps_organico: float, rps_total: float,
                             img_rosca: bytes, img_barra_rps: bytes,
                             img_indice: bytes, ano: int, logo_path: str):
    """Slide 5: Orgânico vs. Total → Web."""
    _fundo_pagina(c, "Organico vs. Total -> Web", logo_path)

    top_y = PAGE_H - 35*mm
    mid = PAGE_W / 2
    col_w = mid * 0.45

    # Rosca + valores
    c.drawImage(_img(img_rosca), 28*mm, top_y - 120,
                width=100, height=100)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(AZUL)
    c.drawString(28*mm + 110, top_y - 55, _fmt_brl(receita_organica))
    c.setFont("Helvetica", 8)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(28*mm + 110, top_y - 68, "receita orgânica")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#212121"))
    c.drawString(28*mm + 110, top_y - 85, _fmt_brl(receita_total))
    c.setFont("Helvetica", 8)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(28*mm + 110, top_y - 98, "receita total do site")

    # Barra RPS
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(colors.HexColor("#212121"))
    c.drawString(28*mm, top_y - 140, "Receita por Sessao - Organico vs. Total")
    c.drawImage(_img(img_barra_rps), 28*mm, top_y - 250,
                width=col_w, height=100)

    # Gráfico índice (direita)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#212121"))
    c.drawString(mid + 5*mm, top_y + 5, "Evolucao Comparativa de Receita")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(mid + 5*mm, top_y - 8, "Comparacao de tendencias")
    c.drawImage(_img(img_indice), mid, top_y - 135,
                width=mid - 40*mm, height=130)

    # Caixas texto
    txt_l = (f"O canal orgânico respondeu por {share_pct:.1f}% da receita total do site. "
             f"Com receita por sessão de R$ {rps_organico:.2f}, quase o dobro da média "
             f"do site (R$ {rps_total:.2f}), o canal reforça sua importância estratégica.")
    txt_r = ("A evolução da receita orgânica permaneceu alinhada à tendência da receita "
             "total do site, acompanhando os principais movimentos sazonais do período.")

    _caixa_texto(c, 25*mm, 12*mm, mid - 35*mm, 50, txt_l)
    _caixa_texto(c, mid, 12*mm, mid - 35*mm, 50, txt_r)
    c.showPage()


def slide_visibilidade_busca_ia(c: canvas.Canvas, kpis_gsc: dict,
                                 dados_ia: dict, img_impressoes: bytes,
                                 img_gauge: bytes, img_serie_ia: bytes,
                                 ano: int, logo_path: str, canal: str = "Varejo"):
    """Slide 6/10: Visibilidade – Busca & IA."""
    _fundo_pagina(c, "Visibilidade - Busca & IA", logo_path)

    mid = PAGE_W / 2
    top_y = PAGE_H - 38*mm
    atual_gsc = kpis_gsc["atual"]

    # KPIs GSC linha
    kpi_data = [
        ("IMPRESSÕES ORGÂNICAS", _fmt_num(atual_gsc["impressoes"]),
         kpis_gsc["var_mom_impressoes"], kpis_gsc["var_yoy_impressoes"]),
        ("POSIÇÃO MÉDIA NO GOOGLE", f"{atual_gsc['posicao']:.1f}", None, None),
        ("CTR ORGÂNICO", f"{atual_gsc['ctr']:.1f}%", None, None),
    ]

    kx = 28*mm
    kw = 90
    kh = 60
    for titulo, valor, var_mom, var_yoy in kpi_data:
        c.setFillColor(BRANCO)
        c.roundRect(kx, top_y - kh, kw, kh, 5, fill=1, stroke=0)
        c.setFont("Helvetica", 7)
        c.setFillColor(CINZA_TEXTO)
        c.drawString(kx + 5, top_y - 14, titulo)
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#212121"))
        c.drawString(kx + 5, top_y - 30, valor)
        if var_mom is not None:
            _badge_variacao(c, kx + 5, top_y - kh + 6, _seta(var_mom), _cor_var(var_mom))
        if var_yoy is not None:
            _badge_variacao(c, kx + 5, top_y - kh + 22, _seta(var_yoy), _cor_var(var_yoy))
        kx += kw + 6

    # Gráfico impressões
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(colors.HexColor("#212121"))
    lbl_ini = f"NOV/{str(ano-1)[2:]} A MAI/{str(ano)[2:]}"
    c.drawString(28*mm, top_y - 75, f"EVOLUÇÃO DE VISIBILIDADE — {lbl_ini}")
    c.drawImage(_img(img_impressoes), 28*mm, top_y - 200,
                width=mid - 38*mm, height=115)

    # IA lado direito
    ia = dados_ia
    mencoes = ia.get("mencoes", {})
    citacoes = ia.get("citacoes", {})
    paginas = ia.get("paginas_citadas", {})
    score = ia.get("score", {}).get("atual", 0)
    label_score = "Alta" if score >= 66 else ("Média" if score >= 33 else "Baixa")

    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#212121"))
    c.drawString(mid + 5*mm, top_y + 5, "Visibilidade na IA")

    # Gauge
    c.drawImage(_img(img_gauge), mid + 5*mm, top_y - 120,
                width=100, height=90)

    # KPIs IA
    ia_kpis = [
        ("Menções", mencoes),
        ("Citações", citacoes),
        ("Páginas citadas", paginas),
    ]
    ix = mid + 5*mm
    for nom, d in ia_kpis:
        v = d.get("atual", 0)
        pct = d.get("variacao_pct", 0)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor("#212121"))
        c.drawString(ix, top_y - 135, f"{_fmt_num(v)}")
        _badge_variacao(c, ix + 35, top_y - 140, _seta(pct), _cor_var(pct))
        c.setFont("Helvetica", 7.5)
        c.setFillColor(CINZA_TEXTO)
        c.drawString(ix, top_y - 147, nom)
        ix += (mid - 20*mm) / 3

    # Série IA
    c.drawImage(_img(img_serie_ia), mid + 5*mm, top_y - 265,
                width=mid - 40*mm, height=110)

    # Rodapé
    c.setFont("Helvetica", 7)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(28*mm, 10, "Dados de visibilidade orgânica — Google Search Console")
    c.showPage()


def slide_visibilidade_keywords(c: canvas.Canvas, total_keywords: int,
                                 top_paginas: list, top_queries: list,
                                 mes_nome: str, ano: int, logo_path: str):
    """Slide 7/11: Palavras-chave, top páginas e top consultas."""
    _fundo_pagina(c, "Visibilidade - Busca & IA", logo_path)

    top_y = PAGE_H - 38*mm
    mid = PAGE_W / 2

    # Card keywords
    c.setFillColor(BRANCO)
    c.roundRect(28*mm, top_y - 40, 140, 35, 5, fill=1, stroke=0)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(34*mm, top_y - 18, "PALAVRAS-CHAVE ATIVAS")
    c.drawString(34*mm, top_y - 27, f"{mes_nome}/{ano}")
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(AZUL)
    c.drawString(120, top_y - 28, _fmt_num(total_keywords))

    # Top Páginas
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#212121"))
    c.drawString(28*mm, top_y - 55, "Top Páginas")

    headers = ["PÁGINA", "IMPRESSÕES", "TIPO"]
    data = [headers] + [
        [p["pagina"][:55], _fmt_num(p["impressoes"]), p["tipo"]]
        for p in top_paginas
    ]
    t = Table(data, colWidths=[mid - 55*mm, 60, 50])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#757575")),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#212121")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRANCO, CINZA_BG]),
        ("GRID", (0, 0), (-1, -1), 0, colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    t.wrapOn(c, mid - 55*mm, 400)
    t.drawOn(c, 28*mm, top_y - 60 - len(data) * 13)

    # Top Consultas (direita)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#212121"))
    c.drawString(mid + 5*mm, top_y - 55, "Top Consultas (sem marca)")

    headers_q = ["CONSULTA", "IMPRESSÕES"]
    data_q = [headers_q] + [
        [q["consulta"], _fmt_num(q["impressoes"])]
        for q in top_queries
    ]
    tq = Table(data_q, colWidths=[mid - 50*mm, 60])
    tq.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#757575")),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#212121")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRANCO, CINZA_BG]),
        ("GRID", (0, 0), (-1, -1), 0, colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    tq.wrapOn(c, mid - 50*mm, 400)
    tq.drawOn(c, mid + 5*mm, top_y - 60 - len(data_q) * 13)

    c.showPage()


def slide_app_bemol(c: canvas.Canvas, kpis_app: dict, img_receita: bytes,
                    mes_nome: str, ano: int, logo_path: str):
    """Slide 8: App Bemol."""
    _fundo_pagina(c, "App Bemol", logo_path)

    top_y = PAGE_H - 38*mm
    mid = PAGE_W / 2

    atual = kpis_app["atual"]
    badge_w = 90
    bx = 28*mm

    # Badge data
    c.setFillColor(AZUL)
    c.roundRect(mid - 50, top_y + 2, 80, 16, 4, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(BRANCO)
    c.drawCentredString(mid - 10, top_y + 7, f"{mes_nome} {ano}")

    # Cards KPI
    kpis_dados = [
        ("RECEITA ORGÂNICA", _fmt_brl(atual["receita"]),
         kpis_app["var_yoy_receita"], kpis_app["var_mom_receita"]),
        ("TRANSAÇÕES", _fmt_num(atual["transacoes"]),
         kpis_app["var_yoy_transacoes"], kpis_app["var_mom_transacoes"]),
        ("USUÁRIOS ATIVOS", _fmt_num(atual["usuarios"]),
         kpis_app["var_yoy_usuarios"], kpis_app["var_mom_usuarios"]),
    ]

    for nom, val, var_yoy, var_mom in kpis_dados:
        c.setFillColor(BRANCO)
        c.roundRect(bx, top_y - 75, badge_w, 70, 5, fill=1, stroke=0)
        c.setFont("Helvetica", 7)
        c.setFillColor(CINZA_TEXTO)
        c.drawString(bx + 5, top_y - 16, nom)
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.HexColor("#212121"))
        c.drawString(bx + 5, top_y - 32, val)
        if var_yoy is not None:
            c.setFont("Helvetica", 7.5)
            c.setFillColor(CINZA_TEXTO)
            c.drawString(bx + 5, top_y - 47, "▼ YoY")
            _badge_variacao(c, bx + 5, top_y - 65, _seta(var_yoy), _cor_var(var_yoy))
        if var_mom is not None:
            _badge_variacao(c, bx + 52, top_y - 65, _seta(var_mom), _cor_var(var_mom))
        bx += badge_w + 6

    # Rosca share
    bx += 10
    c.setFillColor(BRANCO)
    c.roundRect(bx, top_y - 75, 90, 70, 5, fill=1, stroke=0)
    c.setFont("Helvetica", 7)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(bx + 5, top_y - 16, "SHARE ORGÂNICO")
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(AZUL)
    c.drawString(bx + 5, top_y - 36, f"{kpis_app['share_organico']:.1f}%")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(bx + 5, top_y - 50, "da receita total")
    c.drawString(bx + 5, top_y - 60, f"do App em {mes_nome.lower()}/{str(ano)[2:]}")

    # Gráfico receita
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(colors.HexColor("#212121"))
    c.drawString(28*mm, top_y - 90, "EVOLUÇÃO DA RECEITA ORGÂNICA — APP")
    c.drawImage(_img(img_receita), 28*mm, top_y - 220,
                width=PAGE_W - 60*mm, height=120)

    # Caixa texto
    txt = (f"Em {mes_nome}, o canal orgânico do App Bemol apresentou crescimento de "
           f"{abs(kpis_app['var_mom_receita'] or 0):.1f}% na receita, "
           f"{abs(kpis_app['var_mom_transacoes'] or 0):.1f}% nas transações e "
           f"{abs(kpis_app['var_mom_usuarios'] or 0):.1f}% nos usuários ativos. "
           f"O orgânico respondeu por {kpis_app['share_organico']:.1f}% da receita total do App.")
    _caixa_texto(c, 28*mm, 12*mm, PAGE_W - 60*mm, 45, txt)
    c.showPage()


def slide_farma_kpis(c: canvas.Canvas, kpis: dict, mes_nome: str, ano: int,
                      logo_path: str):
    """Slide 9: Performance Orgânica Farma (KPIs)."""
    _fundo_pagina(c, "Performance orgânica", logo_path)

    c.setFont("Helvetica", 9)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(30*mm, PAGE_H - 30*mm, f"mai/{str(ano)[2:]} vs mai/{str(ano-1)[2:]}")

    card_w = (PAGE_W - 70*mm) / 2
    card_h = 90
    gap = 8
    row1_y = PAGE_H - 145
    row2_y = PAGE_H - 145 - card_h - gap
    col1_x = 30*mm
    col2_x = 30*mm + card_w + gap

    atual = kpis["atual"]
    mom = kpis["mom"]
    yoy = kpis["yoy"]

    _card_kpi(c, col1_x, row1_y, card_w, card_h,
              "Sessões Orgânicas", _fmt_num(atual["sessoes"]), "",
              f"VS MAI/{ano-1}", kpis["var_yoy_sessoes"], _fmt_num(yoy["sessoes"]),
              f"VS ABR/{ano} (MOM)", kpis["var_mom_sessoes"], _fmt_num(mom["sessoes"]))

    _card_kpi(c, col2_x, row1_y, card_w, card_h,
              "Taxa de Engajamento", f"{atual['tx_engajamento']:.2f}", "%",
              f"VS MAI/{ano-1}", kpis["var_yoy_tx_eng"], f"{yoy['tx_engajamento']:.2f}%",
              f"VS ABR/{ano} (MOM)", kpis["var_mom_tx_eng"], f"{mom['tx_engajamento']:.2f}%",
              pp=True)

    _card_kpi(c, col1_x, row2_y, card_w, card_h,
              "Receita Orgânica", _fmt_brl(atual["receita"]), "",
              f"VS MAI/{ano-1}", kpis["var_yoy_receita"], _fmt_brl(yoy["receita"]),
              f"VS ABR/{ano} (MOM)", kpis["var_mom_receita"], _fmt_brl(mom["receita"]))

    _card_kpi(c, col2_x, row2_y, card_w, card_h,
              "Total Usuários Orgânicos", _fmt_num(atual["usuarios"]), "",
              f"VS MAI/{ano-1}", kpis["var_yoy_usuarios"], _fmt_num(yoy["usuarios"]),
              f"VS ABR/{ano} (MOM)", kpis["var_mom_usuarios"], _fmt_num(mom["usuarios"]))

    txt = (f"Em {mes_nome}, a Bemol Farma apresentou recuperação com crescimento de "
           f"{abs(kpis['var_mom_sessoes'] or 0):.1f}% nas sessões, "
           f"{abs(kpis['var_mom_usuarios'] or 0):.1f}% nos usuários e "
           f"{abs(kpis['var_mom_receita'] or 0):.1f}% na receita orgânica. "
           "O Organic Search segue como principal canal de aquisição.")
    _caixa_texto(c, 30*mm, 12*mm, PAGE_W - 60*mm, 45, txt)
    c.showPage()


def slide_encerramento(c: canvas.Canvas, mes_nome: str, ano: int):
    """Slide final."""
    c.setFillColor(CINZA_BG)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFont("Helvetica", 14)
    c.setFillColor(AZUL)
    c.drawCentredString(PAGE_W/2, PAGE_H/2,
                        f"Relatório SEO & Search  ·  {mes_nome} / {ano}  ·  Bemol")
    c.showPage()


def criar_pdf(output_path: str, dados: dict, graficos: dict, config: dict):
    """
    Ponto de entrada principal.
    dados: dicionário com todos os dados coletados das APIs
    graficos: dicionário com bytes de cada gráfico PNG
    config: configuração do relatório
    """
    mes = config["relatorio"]["mes"]
    ano = config["relatorio"]["ano"]
    mes_nome = config["relatorio"]["nome_mes"]
    logo_b = config["relatorio"].get("logo_bemol", "")
    logo_f = config["relatorio"].get("logo_farma", "")

    c = canvas.Canvas(output_path, pagesize=landscape(A4))
    c.setTitle(f"Relatório SEO & Search — {mes_nome} {ano}")
    c.setAuthor("Bemol — SEO & Search")

    # Slide 1: Capa
    slide_capa(c, mes_nome, ano, logo_b, logo_f)

    # Slide 2: Visão Geral
    slide_visao_geral(c, dados.get("destaques", []), dados.get("resumo_geral", ""))

    # Slide 3: KPIs Varejo
    slide_performance_web_kpis(c, dados["kpis_varejo"], mes_nome, ano, logo_b)

    # Slide 4: Gráficos Varejo
    slide_performance_web_graficos(
        c, graficos["sessoes_varejo"], graficos["receita_varejo"],
        dados["kpis_varejo"], mes_nome, ano, logo_b)

    # Slide 5: Orgânico vs Total
    slide_organico_vs_total(
        c,
        share_pct=dados["share_varejo"],
        receita_organica=dados["kpis_varejo"]["atual"]["receita"],
        receita_total=dados["receita_total_varejo"],
        rps_organico=dados["rps_organico"],
        rps_total=dados["rps_total"],
        img_rosca=graficos["rosca_varejo"],
        img_barra_rps=graficos["barra_rps"],
        img_indice=graficos["indice_varejo"],
        ano=ano, logo_path=logo_b)

    # Slide 6: Visibilidade Varejo
    slide_visibilidade_busca_ia(
        c, dados["gsc_varejo"], dados["ia_varejo"],
        graficos["impressoes_varejo"], graficos["gauge_varejo"],
        graficos["serie_ia_varejo"], ano, logo_b, "Varejo")

    # Slide 7: Keywords Varejo
    slide_visibilidade_keywords(
        c, dados["keywords_varejo"],
        dados["top_paginas_varejo"], dados["top_queries_varejo"],
        mes_nome, ano, logo_b)

    # Slide 8: App Bemol
    slide_app_bemol(c, dados["kpis_app"], graficos["receita_app"],
                    mes_nome, ano, config["relatorio"].get("logo_app", logo_b))

    # Slide 9: KPIs Farma
    slide_farma_kpis(c, dados["kpis_farma"], mes_nome, ano, logo_f)

    # Slide 10: Visibilidade Farma
    slide_visibilidade_busca_ia(
        c, dados["gsc_farma"], dados["ia_farma"],
        graficos["impressoes_farma"], graficos["gauge_farma"],
        graficos["serie_ia_farma"], ano, logo_f, "Farma")

    # Slide 11: Keywords Farma
    slide_visibilidade_keywords(
        c, dados["keywords_farma"],
        dados["top_paginas_farma"], dados["top_queries_farma"],
        mes_nome, ano, logo_f)

    # Slide 12: Encerramento
    slide_encerramento(c, mes_nome, ano)

    c.save()
    print(f"\n[PDF] Relatório gerado: {output_path}")
