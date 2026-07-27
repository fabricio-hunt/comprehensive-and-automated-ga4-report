"""
Script principal — Gerador Automático do Relatório SEO Bemol.
Nova versão: coleta dados de GA4 e Google Search Console, renderiza HTML
com ECharts e exporta PDF via Playwright.
"""

import json
import sys
import argparse
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from auth import get_credentials
from ga4 import (
    buscar_kpis_organico,
    buscar_serie_mensal,
    buscar_kpis_app,
    buscar_receita_total_web,
    buscar_serie_receita_comparativa,
    buscar_kpis_separados_sem_filtro,
)
from gsc import (
    buscar_kpis_gsc,
    buscar_serie_impressoes,
    buscar_top_paginas,
    buscar_top_queries_sem_marca,
    buscar_total_keywords,
)
from report_data import preparar_contexto_relatorio, montar_payload_relatorio, MESES_CURTOS
from html_renderer import renderizar_relatorio_html, gerar_indice_html
from pdf_exporter import exportar_html_para_pdf

BASE = Path(__file__).parent


def carregar_config(caminho: str = "config.json") -> dict:
    p = BASE / caminho
    if not p.exists():
        print(f"[Erro] Arquivo de configuração não encontrado: {p}")
        sys.exit(1)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _serie_para_lista(serie: dict, metrica: str, mes_atual: int | None = None):
    valores = []
    for mes in range(1, 13):
        valor = serie.get(mes, {}).get(metrica, 0)
        if mes_atual is not None and mes > mes_atual:
            valores.append(None)
        else:
            valores.append(valor)
    return valores


def _calcular_indices(dados_indice: dict, mes_atual: int):
    org_ant = dados_indice.get("organico_ant", [0] * 12)
    tot_ant = dados_indice.get("total_ant", [0] * 12)
    org_at = dados_indice.get("organico_atual", [0] * 12)
    tot_at = dados_indice.get("total_atual", [0] * 12)

    base_org = org_ant[0] or 1
    base_tot = tot_ant[0] or 1

    indice_org = [round(v / base_org * 100, 1) for v in org_ant]
    indice_tot = [round(v / base_tot * 100, 1) for v in tot_ant]

    for i, v in enumerate(org_at, start=1):
        indice_org.append(round(v / base_org * 100, 1) if i <= mes_atual else None)
    for i, v in enumerate(tot_at, start=1):
        indice_tot.append(round(v / base_tot * 100, 1) if i <= mes_atual else None)

    labels = [f"{m}/25" for m in MESES_CURTOS] + [f"{m}/26" for m in MESES_CURTOS]
    return labels, indice_org, indice_tot


def main():
    parser = argparse.ArgumentParser(description="Gerador de Relatório SEO Bemol")
    parser.add_argument("--mes", type=int, help="Mês do relatório (1-12)")
    parser.add_argument("--ano", type=int, help="Ano do relatório")
    parser.add_argument("--mes-anterior", action="store_true", help="Calcula automaticamente o mês anterior a hoje (ideal para rodar todo dia 03 no cron)")
    parser.add_argument("--no-pdf", action="store_true", help="Não gerar arquivo PDF estático (apenas HTML + índice Vercel)")
    parser.add_argument("--config", default="config.json", help="Arquivo de configuração")
    args = parser.parse_args()

    config = carregar_config(args.config)

    if args.mes_anterior:
        hoje = datetime.date.today()
        primeiro_dia_mes_atual = hoje.replace(day=1)
        ultimo_dia_mes_ant = primeiro_dia_mes_atual - datetime.timedelta(days=1)
        config["relatorio"]["mes"] = ultimo_dia_mes_ant.month
        config["relatorio"]["ano"] = ultimo_dia_mes_ant.year
    else:
        if args.mes:
            config["relatorio"]["mes"] = args.mes
        if args.ano:
            config["relatorio"]["ano"] = args.ano

    contexto = preparar_contexto_relatorio(config)
    mes = contexto.mes
    ano = contexto.ano

    print("=" * 60)
    print(f"  Relatório SEO Bemol — {contexto.mes_nome} / {ano}")
    print("=" * 60)

    print("\n[1/4] Autenticando...")
    creds = get_credentials(str(BASE / config["credencial_oauth"]))

    prop_varejo_app = config["ga4"]["property_varejo_app"]
    prop_farma = config["ga4"]["property_farma"]
    plat_varejo = config["ga4"].get("plataforma_varejo", "WEB")
    plat_app = config["ga4"].get("plataforma_app", "APP")

    site_v = config["search_console"]["site_url_varejo"]
    site_f = config["search_console"]["site_url_farma"]

    print("\n[2/4] Coletando dados das APIs...")
    kpis_varejo = buscar_kpis_organico(creds, prop_varejo_app, mes, ano, plat_varejo)
    serie_varejo_at = buscar_serie_mensal(creds, prop_varejo_app, ano, plat_varejo, organico=True)
    serie_varejo_ant = buscar_serie_mensal(creds, prop_varejo_app, ano - 1, plat_varejo, organico=True)
    dados_total_web = buscar_receita_total_web(creds, prop_varejo_app, mes, ano)

    kpis_separados = buscar_kpis_separados_sem_filtro(creds, prop_varejo_app, prop_farma, mes, ano)

    kpis_app = buscar_kpis_app(creds, prop_varejo_app, mes, ano)
    serie_app_at = buscar_serie_mensal(creds, prop_varejo_app, ano, plat_app, organico=True)
    serie_app_ant = buscar_serie_mensal(creds, prop_varejo_app, ano - 1, plat_app, organico=True)

    dados_indice = buscar_serie_receita_comparativa(creds, prop_varejo_app, ano)

    kpis_farma = buscar_kpis_organico(creds, prop_farma, mes, ano, plataforma=None)

    gsc_varejo = buscar_kpis_gsc(creds, site_v, mes, ano)
    serie_imp_varejo = buscar_serie_impressoes(creds, site_v, mes, ano)
    top_pag_varejo = buscar_top_paginas(creds, site_v, mes, ano, top_n=10)
    top_q_varejo = buscar_top_queries_sem_marca(creds, site_v, mes, ano, top_n=10)
    kw_varejo = buscar_total_keywords(creds, site_v, mes, ano)

    gsc_farma = buscar_kpis_gsc(creds, site_f, mes, ano)
    serie_imp_farma = buscar_serie_impressoes(creds, site_f, mes, ano)
    top_pag_farma = buscar_top_paginas(creds, site_f, mes, ano, top_n=10)
    top_q_farma = buscar_top_queries_sem_marca(
        creds,
        site_f,
        mes,
        ano,
        top_n=10,
        termos_marca=["bemol farma", "bemolfarma"],
    )
    kw_farma = buscar_total_keywords(creds, site_f, mes, ano)

    rec_org = kpis_varejo["atual"]["receita"]
    sess_org = kpis_varejo["atual"]["sessoes"]
    receita_total_varejo = dados_total_web["receita"]
    sessoes_total_web = dados_total_web["sessoes"]
    rps_organico = rec_org / sess_org if sess_org > 0 else 0
    rps_total = receita_total_varejo / sessoes_total_web if sessoes_total_web > 0 else 0
    share_varejo = rec_org / receita_total_varejo * 100 if receita_total_varejo > 0 else 0

    index_labels, indice_org, indice_total = _calcular_indices(dados_indice, mes)

    dados_brutos = {
        "kpis_separados": kpis_separados,
        "kpis_varejo": kpis_varejo,
        "kpis_farma": kpis_farma,
        "kpis_app": kpis_app,
        "gsc_varejo": gsc_varejo,
        "gsc_farma": gsc_farma,
        "share_varejo": share_varejo,
        "receita_total_varejo": receita_total_varejo,
        "rps_organico": rps_organico,
        "rps_total": rps_total,
        "keywords_varejo": kw_varejo,
        "keywords_farma": kw_farma,
        "top_paginas_varejo": top_pag_varejo,
        "top_queries_varejo": top_q_varejo,
        "top_paginas_farma": top_pag_farma,
        "top_queries_farma": top_q_farma,
        "charts": {
            "meta": {"ano": ano},
            "labels12": MESES_CURTOS,
            "web_sessions_current": _serie_para_lista(serie_varejo_at, "sessoes", mes),
            "web_sessions_previous": _serie_para_lista(serie_varejo_ant, "sessoes"),
            "web_revenue_current": _serie_para_lista(serie_varejo_at, "receita", mes),
            "web_revenue_previous": _serie_para_lista(serie_varejo_ant, "receita"),
            "web_share": round(share_varejo, 1),
            "web_rps_organico": round(rps_organico, 2),
            "web_rps_total": round(rps_total, 2),
            "index_labels": index_labels,
            "web_index_organico": indice_org,
            "web_index_total": indice_total,
            "web_impressions_labels": serie_imp_varejo["labels"],
            "web_impressions_values": serie_imp_varejo["impressoes"],
            "app_revenue_current": _serie_para_lista(serie_app_at, "receita", mes),
            "app_revenue_previous": _serie_para_lista(serie_app_ant, "receita"),
            "farma_impressions_labels": serie_imp_farma["labels"],
            "farma_impressions_values": serie_imp_farma["impressoes"],
        },
    }

    print("\n[3/4] Renderizando HTML...")
    payload = montar_payload_relatorio(contexto, dados_brutos)

    output_dir = BASE / "output"
    output_dir.mkdir(exist_ok=True)

    html_path = output_dir / f"Relatorio_SEO_{contexto.mes_nome}_{ano}.html"
    pdf_path = output_dir / f"Relatorio_SEO_{contexto.mes_nome}_{ano}.pdf"

    renderizar_relatorio_html(payload, str(html_path))

    if not args.no_pdf:
        print("\n[4/4] Exportando PDF...")
        exportar_html_para_pdf(str(html_path), str(pdf_path))
    else:
        print("\n[4/4] Geração de PDF estático ignorada (--no-pdf).")

    print("\n[Vercel] Gerando índice de relatórios em output/index.html...")
    index_path = gerar_indice_html(output_dir)

    print("\nConcluído!")
    print(f"HTML gerado em: {html_path}")
    if not args.no_pdf:
        print(f"PDF gerado em: {pdf_path}")
    print(f"Portal índice gerado em: {index_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
