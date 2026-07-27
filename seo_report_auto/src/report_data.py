from __future__ import annotations

from dataclasses import dataclass
from typing import Any


MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

MESES_CURTOS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


@dataclass
class ReportContext:
    config: dict[str, Any]
    mes: int
    ano: int
    mes_nome: str
    mes_abrev: str


def preparar_contexto_relatorio(config: dict[str, Any]) -> ReportContext:
    mes = config["relatorio"]["mes"]
    ano = config["relatorio"]["ano"]
    mes_nome = MESES_PT[mes - 1]
    config["relatorio"]["nome_mes"] = mes_nome
    return ReportContext(
        config=config,
        mes=mes,
        ano=ano,
        mes_nome=mes_nome,
        mes_abrev=MESES_CURTOS[mes - 1],
    )


def _safe_pct(value: float | None) -> float:
    return 0.0 if value is None else float(value)


def _fmt_num(v: float | int) -> str:
    return f"{v:,.0f}".replace(",", ".")


def _fmt_decimal(v: float, casas: int = 1) -> str:
    return f"{v:.{casas}f}".replace(".", ",")


def _fmt_brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_brl_compacto(v: float) -> str:
    if abs(v) >= 1_000_000:
        return f"R$ {_fmt_decimal(v / 1_000_000, 1)} mi"
    if abs(v) >= 1_000:
        return f"R$ {_fmt_decimal(v / 1_000, 0)} mil"
    return _fmt_brl(v)


def _delta_class(v: float | None, invert: bool = False) -> str:
    if v is None:
        return "neutral"
    positivo = v < 0 if invert else v >= 0
    return "up" if positivo else "down"


def _delta_text(v: float | None, suffix: str = "%", invert: bool = False) -> str:
    if v is None:
        return "-"
    positivo = v < 0 if invert else v >= 0
    seta = "↑" if positivo else "↓"
    return f"{seta} {_fmt_decimal(abs(v), 1)}{suffix}"


def _card_metric(title: str, value: str, yoy_label: str, yoy_value: str, yoy_var: float | None,
                 mom_label: str, mom_value: str, mom_var: float | None, invert_delta: bool = False,
                 suffix: str = "%") -> dict[str, Any]:
    return {
        "title": title,
        "value": value,
        "yoy": {
            "label": yoy_label,
            "value": yoy_value,
            "delta": _delta_text(yoy_var, suffix=suffix, invert=invert_delta),
            "class": _delta_class(yoy_var, invert=invert_delta),
        },
        "mom": {
            "label": mom_label,
            "value": mom_value,
            "delta": _delta_text(mom_var, suffix=suffix, invert=invert_delta),
            "class": _delta_class(mom_var, invert=invert_delta),
        },
    }


def _frase_resultado(nome: str, variacao: float | None, unidade: str = "%") -> str:
    if variacao is None:
        return f"{nome} ficou estável no período."
    if variacao >= 0:
        return f"{nome} avançou {_fmt_decimal(abs(variacao), 1)}{unidade}, com leitura positiva no período."
    return f"{nome} recuou {_fmt_decimal(abs(variacao), 1)}{unidade}, mantendo oportunidade de recuperação no próximo ciclo."


def gerar_destaques(kpis_varejo: dict[str, Any], kpis_app: dict[str, Any],
                    kpis_farma: dict[str, Any]) -> list[str]:
    destaques: list[str] = []

    rec_v = kpis_varejo["atual"]["receita"]
    destaques.append(
        f"Varejo: receita orgânica atingiu {_fmt_brl_compacto(rec_v)}, com variação de "
        f"{_fmt_decimal(abs(_safe_pct(kpis_varejo['var_mom_receita'])), 1)}% vs. mês anterior e "
        f"{_fmt_decimal(abs(_safe_pct(kpis_varejo['var_yoy_receita'])), 1)}% vs. mesmo mês do ano anterior."
    )

    destaques.append(
        f"No Varejo Web, sessões ({_fmt_decimal(_safe_pct(kpis_varejo['var_mom_sessoes']), 1)}%), "
        f"usuários ({_fmt_decimal(_safe_pct(kpis_varejo['var_mom_usuarios']), 1)}%) e engajamento "
        f"({_fmt_decimal(_safe_pct(kpis_varejo['var_mom_tx_eng']), 1)} p.p.) evoluíram no comparativo mensal."
    )

    destaques.append(
        f"No App Bemol, o canal orgânico variou {_fmt_decimal(_safe_pct(kpis_app['var_mom_receita']), 1)}% em receita, "
        f"{_fmt_decimal(_safe_pct(kpis_app['var_mom_transacoes']), 1)}% em transações e "
        f"{_fmt_decimal(_safe_pct(kpis_app['var_mom_usuarios']), 1)}% em usuários ativos, representando "
        f"{_fmt_decimal(kpis_app['share_organico'], 1)}% da receita total do aplicativo."
    )

    destaques.append(
        f"A Bemol Farma apresentou variação mensal de {_fmt_decimal(_safe_pct(kpis_farma['var_mom_sessoes']), 1)}% em sessões, "
        f"{_fmt_decimal(_safe_pct(kpis_farma['var_mom_usuarios']), 1)}% em usuários e "
        f"{_fmt_decimal(_safe_pct(kpis_farma['var_mom_receita']), 1)}% em receita orgânica."
    )

    return destaques


def montar_payload_relatorio(contexto: ReportContext, dados_brutos: dict[str, Any]) -> dict[str, Any]:
    ano = contexto.ano
    mes_nome = contexto.mes_nome
    mes_abrev = contexto.mes_abrev

    kpis_separados = dados_brutos["kpis_separados"]
    kpis_varejo = dados_brutos["kpis_varejo"]
    kpis_farma = dados_brutos["kpis_farma"]
    kpis_app = dados_brutos["kpis_app"]
    gsc_varejo = dados_brutos["gsc_varejo"]
    gsc_farma = dados_brutos["gsc_farma"]

    destaques = gerar_destaques(kpis_varejo, kpis_app, kpis_farma)

    resumo_geral = (
        f"{mes_nome} consolidou o acompanhamento da performance do ecossistema Bemol, "
        f"com leitura integrada de Web, App e Farma a partir de dados do GA4 e Google Search Console."
    )

    comparativo_curto = f"{mes_abrev.lower()}/{str(ano)[2:]} vs {mes_abrev.lower()}/{str(ano - 1)[2:]}"

    share_varejo = dados_brutos["share_varejo"]
    receita_total_varejo = dados_brutos["receita_total_varejo"]
    rps_organico = dados_brutos["rps_organico"]
    rps_total = dados_brutos["rps_total"]

    def _build_cards(kpi_data: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            _card_metric(
                "Sessões",
                _fmt_num(kpi_data["atual"]["sessoes"]),
                f"YOY · vs {mes_abrev}/{ano - 1}",
                _fmt_num(kpi_data["yoy"]["sessoes"]),
                kpi_data["var_yoy_sessoes"],
                f"MOM · vs mês anterior",
                _fmt_num(kpi_data["mom"]["sessoes"]),
                kpi_data["var_mom_sessoes"],
            ),
            _card_metric(
                "Usuários",
                _fmt_num(kpi_data["atual"]["usuarios"]),
                f"YOY · vs {mes_abrev}/{ano - 1}",
                _fmt_num(kpi_data["yoy"]["usuarios"]),
                kpi_data["var_yoy_usuarios"],
                f"MOM · vs mês anterior",
                _fmt_num(kpi_data["mom"]["usuarios"]),
                kpi_data["var_mom_usuarios"],
            ),
            _card_metric(
                "Receita",
                _fmt_brl(kpi_data["atual"]["receita"]),
                f"YOY · vs {mes_abrev}/{ano - 1}",
                _fmt_brl(kpi_data["yoy"]["receita"]),
                kpi_data["var_yoy_receita"],
                "MOM · vs mês anterior",
                _fmt_brl(kpi_data["mom"]["receita"]),
                kpi_data["var_mom_receita"],
            ),
            _card_metric(
                "Tx. Engajamento",
                f"{_fmt_decimal(kpi_data['atual']['tx_engajamento'], 2)}%",
                f"YOY · vs {mes_abrev}/{ano - 1}",
                f"{_fmt_decimal(kpi_data['yoy']['tx_engajamento'], 2)}%",
                kpi_data["var_yoy_tx_eng"],
                "MOM · vs mês anterior",
                f"{_fmt_decimal(kpi_data['mom']['tx_engajamento'], 2)}%",
                kpi_data["var_mom_tx_eng"],
                suffix=" p.p.",
            ),
        ]

    payload = {
        "meta": {
            "mes": contexto.mes,
            "ano": ano,
            "mes_nome": mes_nome,
            "nome_mes": mes_nome,
            "mes_abrev": mes_abrev,
            "titulo": f"Relatório SEO & Search - {mes_nome} / {ano}",
            "subtitle": "Bemol Varejo · Bemol Farma · App Bemol",
            "comparativo_curto": comparativo_curto,
        },
        "branding": {
            "logo_bemol": contexto.config["relatorio"].get("logo_bemol", ""),
            "logo_farma": contexto.config["relatorio"].get("logo_farma", ""),
            "logo_app": contexto.config["relatorio"].get("logo_app", contexto.config["relatorio"].get("logo_bemol", "")),
        },
        "executive_summary": {
            "resumo": resumo_geral,
            "highlights": destaques,
        },
        "charts": dados_brutos["charts"],
        "geral": {
            "web_cards": _build_cards(kpis_separados["web"]),
            "app_cards": _build_cards(kpis_separados["app"]),
            "farma_cards": _build_cards(kpis_separados["farma"]),
        },
        "web": {
            "cards": [
                _card_metric(
                    "Sessões orgânicas",
                    _fmt_num(kpis_varejo["atual"]["sessoes"]),
                    f"YoY · vs {mes_abrev}/{ano - 1}",
                    _fmt_num(kpis_varejo["yoy"]["sessoes"]),
                    kpis_varejo["var_yoy_sessoes"],
                    f"MoM · vs mês anterior",
                    _fmt_num(kpis_varejo["mom"]["sessoes"]),
                    kpis_varejo["var_mom_sessoes"],
                ),
                _card_metric(
                    "Taxa de engajamento",
                    f"{_fmt_decimal(kpis_varejo['atual']['tx_engajamento'], 2)}%",
                    f"YoY · vs {mes_abrev}/{ano - 1}",
                    f"{_fmt_decimal(kpis_varejo['yoy']['tx_engajamento'], 2)}%",
                    kpis_varejo["var_yoy_tx_eng"],
                    "MoM · vs mês anterior",
                    f"{_fmt_decimal(kpis_varejo['mom']['tx_engajamento'], 2)}%",
                    kpis_varejo["var_mom_tx_eng"],
                    suffix=" p.p.",
                ),
                _card_metric(
                    "Receita orgânica",
                    _fmt_brl(kpis_varejo["atual"]["receita"]),
                    f"YoY · vs {mes_abrev}/{ano - 1}",
                    _fmt_brl(kpis_varejo["yoy"]["receita"]),
                    kpis_varejo["var_yoy_receita"],
                    "MoM · vs mês anterior",
                    _fmt_brl(kpis_varejo["mom"]["receita"]),
                    kpis_varejo["var_mom_receita"],
                ),
                _card_metric(
                    "Usuários orgânicos",
                    _fmt_num(kpis_varejo["atual"]["usuarios"]),
                    f"YoY · vs {mes_abrev}/{ano - 1}",
                    _fmt_num(kpis_varejo["yoy"]["usuarios"]),
                    kpis_varejo["var_yoy_usuarios"],
                    "MoM · vs mês anterior",
                    _fmt_num(kpis_varejo["mom"]["usuarios"]),
                    kpis_varejo["var_mom_usuarios"],
                ),
            ],
            "commentary": [
                f"{mes_nome} registrou {_fmt_num(kpis_varejo['atual']['sessoes'])} sessões orgânicas no Varejo Web e receita de {_fmt_brl(kpis_varejo['atual']['receita'])}.",
                _frase_resultado("A receita orgânica", kpis_varejo["var_mom_receita"]),
                _frase_resultado("As sessões orgânicas", kpis_varejo["var_mom_sessoes"]),
                f"A taxa de engajamento fechou em {_fmt_decimal(kpis_varejo['atual']['tx_engajamento'], 2)}%.",
            ],
            "graph_notes": {
                "sessoes": _frase_resultado("Sessões orgânicas no Varejo Web", kpis_varejo["var_mom_sessoes"]),
                "receita": _frase_resultado("Receita orgânica no Varejo Web", kpis_varejo["var_mom_receita"]),
                "share": f"O orgânico respondeu por {_fmt_decimal(share_varejo, 1)}% da receita total do site no período.",
                "rps": (
                    f"A receita por sessão ficou em {_fmt_brl(rps_organico)} no orgânico, "
                    f"acima da média total de {_fmt_brl(rps_total)}."
                    if rps_organico >= rps_total
                    else f"A receita por sessão ficou em {_fmt_brl(rps_organico)} no orgânico, abaixo da média total de {_fmt_brl(rps_total)}."
                ),
                "indice": "O índice comparativo mostra a evolução da receita orgânica frente ao total do site ao longo da série histórica.",
                "impressoes": _frase_resultado("Impressões orgânicas no Google", gsc_varejo["var_mom_impressoes"]),
            },
            "share": {
                "organico": _fmt_brl(kpis_varejo["atual"]["receita"]),
                "total": _fmt_brl(receita_total_varejo),
                "percentual": _fmt_decimal(share_varejo, 1),
                "rps_organico": _fmt_brl(rps_organico),
                "rps_total": _fmt_brl(rps_total),
            },
            "search": {
                "cards": [
                    {
                        "title": "Impressões orgânicas",
                        "value": _fmt_num(gsc_varejo['atual']['impressoes']),
                        "mom": _delta_text(gsc_varejo['var_mom_impressoes']),
                        "mom_class": _delta_class(gsc_varejo['var_mom_impressoes']),
                        "yoy": _delta_text(gsc_varejo['var_yoy_impressoes']),
                        "yoy_class": _delta_class(gsc_varejo['var_yoy_impressoes']),
                    },
                    {
                        "title": "Cliques orgânicos",
                        "value": _fmt_num(gsc_varejo['atual']['cliques']),
                    },
                    {
                        "title": "CTR orgânico",
                        "value": f"{_fmt_decimal(gsc_varejo['atual']['ctr'], 1)}%",
                    },
                    {
                        "title": "Posição média",
                        "value": _fmt_decimal(gsc_varejo['atual']['posicao'], 1),
                    },
                ],
                "keywords": _fmt_num(dados_brutos['keywords_varejo']),
                "top_pages": dados_brutos['top_paginas_varejo'],
                "top_queries": dados_brutos['top_queries_varejo'],
            },
        },
        "app": {
            "comparison_label": comparativo_curto,
            "cards": [
                {
                    "title": "Receita orgânica",
                    "value": _fmt_brl(kpis_app['atual']['receita']),
                    "yoy": _delta_text(kpis_app['var_yoy_receita']),
                    "yoy_class": _delta_class(kpis_app['var_yoy_receita']),
                    "mom": _delta_text(kpis_app['var_mom_receita']),
                    "mom_class": _delta_class(kpis_app['var_mom_receita']),
                },
                {
                    "title": "Transações",
                    "value": _fmt_num(kpis_app['atual']['transacoes']),
                    "yoy": _delta_text(kpis_app['var_yoy_transacoes']),
                    "yoy_class": _delta_class(kpis_app['var_yoy_transacoes']),
                    "mom": _delta_text(kpis_app['var_mom_transacoes']),
                    "mom_class": _delta_class(kpis_app['var_mom_transacoes']),
                },
                {
                    "title": "Usuários ativos",
                    "value": _fmt_num(kpis_app['atual']['usuarios']),
                    "yoy": _delta_text(kpis_app['var_yoy_usuarios']),
                    "yoy_class": _delta_class(kpis_app['var_yoy_usuarios']),
                    "mom": _delta_text(kpis_app['var_mom_usuarios']),
                    "mom_class": _delta_class(kpis_app['var_mom_usuarios']),
                },
                {
                    "title": "Share orgânico",
                    "value": f"{_fmt_decimal(kpis_app['share_organico'], 1)}%",
                    "description": "da receita total do app",
                },
            ],
            "commentary": (
                f"Em {mes_nome}, o canal orgânico do App Bemol registrou {_fmt_brl(kpis_app['atual']['receita'])} em receita e "
                f"{_fmt_num(kpis_app['atual']['transacoes'])} transações, com share de {_fmt_decimal(kpis_app['share_organico'], 1)}% da receita total do aplicativo."
            ),
            "graph_note": _frase_resultado("Receita orgânica do App", kpis_app["var_mom_receita"]),
        },
        "farma": {
            "cards": [
                _card_metric(
                    "Sessões orgânicas",
                    _fmt_num(kpis_farma["atual"]["sessoes"]),
                    f"YoY · vs {mes_abrev}/{ano - 1}",
                    _fmt_num(kpis_farma["yoy"]["sessoes"]),
                    kpis_farma["var_yoy_sessoes"],
                    "MoM · vs mês anterior",
                    _fmt_num(kpis_farma["mom"]["sessoes"]),
                    kpis_farma["var_mom_sessoes"],
                ),
                _card_metric(
                    "Taxa de engajamento",
                    f"{_fmt_decimal(kpis_farma['atual']['tx_engajamento'], 2)}%",
                    f"YoY · vs {mes_abrev}/{ano - 1}",
                    f"{_fmt_decimal(kpis_farma['yoy']['tx_engajamento'], 2)}%",
                    kpis_farma["var_yoy_tx_eng"],
                    "MoM · vs mês anterior",
                    f"{_fmt_decimal(kpis_farma['mom']['tx_engajamento'], 2)}%",
                    kpis_farma["var_mom_tx_eng"],
                    suffix=" p.p.",
                ),
                _card_metric(
                    "Receita orgânica",
                    _fmt_brl(kpis_farma["atual"]["receita"]),
                    f"YoY · vs {mes_abrev}/{ano - 1}",
                    _fmt_brl(kpis_farma["yoy"]["receita"]),
                    kpis_farma["var_yoy_receita"],
                    "MoM · vs mês anterior",
                    _fmt_brl(kpis_farma["mom"]["receita"]),
                    kpis_farma["var_mom_receita"],
                ),
                _card_metric(
                    "Usuários orgânicos",
                    _fmt_num(kpis_farma["atual"]["usuarios"]),
                    f"YoY · vs {mes_abrev}/{ano - 1}",
                    _fmt_num(kpis_farma["yoy"]["usuarios"]),
                    kpis_farma["var_yoy_usuarios"],
                    "MoM · vs mês anterior",
                    _fmt_num(kpis_farma["mom"]["usuarios"]),
                    kpis_farma["var_mom_usuarios"],
                ),
            ],
            "commentary": [
                f"A Bemol Farma registrou {_fmt_num(kpis_farma['atual']['sessoes'])} sessões orgânicas e {_fmt_brl(kpis_farma['atual']['receita'])} em receita orgânica no período.",
                _frase_resultado("A receita orgânica da Farma", kpis_farma["var_mom_receita"]),
                _frase_resultado("As sessões orgânicas da Farma", kpis_farma["var_mom_sessoes"]),
                f"A taxa de engajamento ficou em {_fmt_decimal(kpis_farma['atual']['tx_engajamento'], 2)}%.",
            ],
            "graph_notes": {
                "impressoes": _frase_resultado("Impressões orgânicas da Farma", gsc_farma["var_mom_impressoes"]),
            },
            "search": {
                "cards": [
                    {
                        "title": "Impressões orgânicas",
                        "value": _fmt_num(gsc_farma['atual']['impressoes']),
                        "mom": _delta_text(gsc_farma['var_mom_impressoes']),
                        "mom_class": _delta_class(gsc_farma['var_mom_impressoes']),
                        "yoy": _delta_text(gsc_farma['var_yoy_impressoes']),
                        "yoy_class": _delta_class(gsc_farma['var_yoy_impressoes']),
                    },
                    {
                        "title": "Cliques orgânicos",
                        "value": _fmt_num(gsc_farma['atual']['cliques']),
                    },
                    {
                        "title": "CTR orgânico",
                        "value": f"{_fmt_decimal(gsc_farma['atual']['ctr'], 1)}%",
                    },
                    {
                        "title": "Posição média",
                        "value": _fmt_decimal(gsc_farma['atual']['posicao'], 1),
                    },
                ],
                "keywords": _fmt_num(dados_brutos['keywords_farma']),
                "top_pages": dados_brutos['top_paginas_farma'],
                "top_queries": dados_brutos['top_queries_farma'],
            },
        },
    }

    return payload
