"""
Busca dados do GA4 via Data API.

Estrutura de propriedades:
  - 272846783  → Ecommerce Bemol (Varejo WEB + App)
                 Filtro por dimensão 'platform': WEB ou APP
  - 374507459  → Bemol Farma (propriedade dedicada, sem filtro de plataforma)

Retorna dicionários estruturados prontos para o gerador de gráficos/PDF.
"""

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, DateRange, Metric, Dimension,
    FilterExpression, FilterExpressionList, Filter,
    MetricAggregation
)
from google.oauth2.credentials import Credentials


# ── Cliente ───────────────────────────────────────────────────────────────────

def _client(creds: Credentials) -> BetaAnalyticsDataClient:
    return BetaAnalyticsDataClient(credentials=creds)


# ── Intervalos de datas ───────────────────────────────────────────────────────

def _periodo(mes: int, ano: int):
    inicio = date(ano, mes, 1)
    fim = (inicio + relativedelta(months=1)) - timedelta(days=1)
    return inicio.strftime("%Y-%m-%d"), fim.strftime("%Y-%m-%d")


def _periodo_anterior(mes: int, ano: int):
    ref = date(ano, mes, 1) - relativedelta(months=1)
    return _periodo(ref.month, ref.year)


def _mesmo_mes_ano_anterior(mes: int, ano: int):
    return _periodo(mes, ano - 1)


# ── Helpers de filtro ─────────────────────────────────────────────────────────

def _filtro_plataforma(plataforma: str) -> FilterExpression:
    """
    Filtra pela dimensão 'platform'.
    plataforma: 'WEB' para varejo web, 'APP' para app (iOS + Android).
    """
    if plataforma == "APP":
        # Android e iOS — usamos filtro IN (ou dois OR)
        return FilterExpression(
            or_group=FilterExpressionList(expressions=[
                FilterExpression(filter=Filter(
                    field_name="platform",
                    string_filter=Filter.StringFilter(value="iOS")
                )),
                FilterExpression(filter=Filter(
                    field_name="platform",
                    string_filter=Filter.StringFilter(value="Android")
                )),
            ])
        )
    # WEB
    return FilterExpression(
        filter=Filter(
            field_name="platform",
            string_filter=Filter.StringFilter(value="WEB")
        )
    )


def _filtro_organico() -> FilterExpression:
    return FilterExpression(
        filter=Filter(
            field_name="sessionDefaultChannelGrouping",
            string_filter=Filter.StringFilter(value="Organic Search")
        )
    )


def _combinar(f1: FilterExpression, f2: FilterExpression) -> FilterExpression:
    if f1 and f2:
        return FilterExpression(
            and_group=FilterExpressionList(expressions=[f1, f2])
        )
    return f1 or f2


# ── Runner genérico ───────────────────────────────────────────────────────────

def _run(client, property_id, start, end, metrics,
         dimension_filter=None, limit=1):
    req = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        metrics=[Metric(name=m) for m in metrics],
        dimension_filter=dimension_filter,
        limit=limit,
        metric_aggregations=[MetricAggregation.TOTAL],
    )
    return client.run_report(req)


def _total(response, idx: int = 0) -> float:
    try:
        return float(response.totals[0].metric_values[idx].value)
    except (IndexError, ValueError):
        return 0.0


# ── KPIs orgânicos (Varejo Web ou Farma) ─────────────────────────────────────

def buscar_kpis_organico(creds, property_id, mes, ano, plataforma: str = None):
    """
    Retorna KPIs orgânicos: sessões, usuários, receita, taxa de engajamento.
    + variações MoM e YoY.

    plataforma: 'WEB' para Varejo (prop. 272846783),
                None para Farma (prop. 374507459 — sem filtro de plataforma).
    """
    client = _client(creds)

    f_org = _filtro_organico()
    f_plat = _filtro_plataforma(plataforma) if plataforma else None
    filtro = _combinar(f_plat, f_org)

    def fetch(start, end):
        r = _run(client, property_id, start, end,
                 ["sessions", "totalUsers", "purchaseRevenue", "engagedSessions"],
                 dimension_filter=filtro)
        sessoes = _total(r, 0)
        usuarios = _total(r, 1)
        receita = _total(r, 2)
        eng = _total(r, 3)
        tx_eng = (eng / sessoes * 100) if sessoes > 0 else 0.0
        return {"sessoes": sessoes, "usuarios": usuarios,
                "receita": receita, "tx_engajamento": tx_eng}

    atual_s, atual_e = _periodo(mes, ano)
    mom_s, mom_e = _periodo_anterior(mes, ano)
    yoy_s, yoy_e = _mesmo_mes_ano_anterior(mes, ano)

    tag = f"prop={property_id}" + (f" plat={plataforma}" if plataforma else " farma")
    print(f"  [GA4] KPIs organicos ({tag}): {atual_s} -> {atual_e}")

    atual = fetch(atual_s, atual_e)
    mom = fetch(mom_s, mom_e)
    yoy = fetch(yoy_s, yoy_e)

    def pct(novo, antigo):
        return round((novo - antigo) / antigo * 100, 1) if antigo else None

    return {
        "atual": atual,
        "mom": mom,
        "yoy": yoy,
        "var_mom_sessoes":   pct(atual["sessoes"],        mom["sessoes"]),
        "var_yoy_sessoes":   pct(atual["sessoes"],        yoy["sessoes"]),
        "var_mom_usuarios":  pct(atual["usuarios"],       mom["usuarios"]),
        "var_yoy_usuarios":  pct(atual["usuarios"],       yoy["usuarios"]),
        "var_mom_receita":   pct(atual["receita"],        mom["receita"]),
        "var_yoy_receita":   pct(atual["receita"],        yoy["receita"]),
        "var_mom_tx_eng":    round(atual["tx_engajamento"] - mom["tx_engajamento"], 1),
        "var_yoy_tx_eng":    round(atual["tx_engajamento"] - yoy["tx_engajamento"], 1),
    }


# ── Série mensal (jan–dez) ────────────────────────────────────────────────────

def buscar_serie_mensal(creds, property_id, ano,
                         plataforma: str = None, organico: bool = True):
    """
    Série histórica de sessões e receita para todos os meses do ano.
    plataforma: 'WEB' | 'APP' | None (Farma)
    organico: True → filtra Organic Search; False → todos os canais
    """
    client = _client(creds)

    f_plat = _filtro_plataforma(plataforma) if plataforma else None
    f_org = _filtro_organico() if organico else None
    filtro = _combinar(f_plat, f_org)

    today = date.today()
    resultados = {}
    for mes in range(1, 13):
        start, end = _periodo(mes, ano)
        if date.fromisoformat(end) > today:
            resultados[mes] = {"sessoes": 0, "receita": 0}
            continue
        try:
            r = _run(client, property_id, start, end,
                     ["sessions", "purchaseRevenue"],
                     dimension_filter=filtro)
            resultados[mes] = {"sessoes": _total(r, 0), "receita": _total(r, 1)}
        except Exception as e:
            print(f"  [GA4] Aviso: erro ao buscar mes {mes}/{ano}: {e}")
            resultados[mes] = {"sessoes": 0, "receita": 0}
    return resultados


# ── KPIs App Bemol ────────────────────────────────────────────────────────────

def buscar_kpis_app(creds, property_id, mes, ano):
    """
    KPIs App Bemol (filtro platform=APP):
    receita orgânica, transações, usuários ativos + share da receita total do App.
    """
    client = _client(creds)

    f_app = _filtro_plataforma("APP")
    f_org = _filtro_organico()
    filtro_org = _combinar(f_app, f_org)

    def fetch_org(start, end):
        r = _run(client, property_id, start, end,
                 ["sessions", "totalUsers", "purchaseRevenue", "transactions"],
                 dimension_filter=filtro_org)
        return {
            "sessoes":    _total(r, 0),
            "usuarios":   _total(r, 1),
            "receita":    _total(r, 2),
            "transacoes": _total(r, 3),
        }

    def fetch_total_app(start, end):
        """Receita total do App (todos os canais)."""
        r = _run(client, property_id, start, end,
                 ["purchaseRevenue"],
                 dimension_filter=f_app)
        return _total(r, 0)

    atual_s, atual_e = _periodo(mes, ano)
    mom_s, mom_e = _periodo_anterior(mes, ano)
    yoy_s, yoy_e = _mesmo_mes_ano_anterior(mes, ano)

    print(f"  [GA4] KPIs App Bemol: {atual_s} -> {atual_e}")

    atual = fetch_org(atual_s, atual_e)
    mom   = fetch_org(mom_s, mom_e)
    yoy   = fetch_org(yoy_s, yoy_e)
    receita_total = fetch_total_app(atual_s, atual_e)

    def pct(novo, antigo):
        return round((novo - antigo) / antigo * 100, 1) if antigo else None

    share = round(atual["receita"] / receita_total * 100, 1) if receita_total else 0.0

    return {
        "atual": atual,
        "mom": mom,
        "yoy": yoy,
        "share_organico":      share,
        "receita_total_app":   receita_total,
        "var_mom_receita":     pct(atual["receita"],    mom["receita"]),
        "var_yoy_receita":     pct(atual["receita"],    yoy["receita"]),
        "var_mom_transacoes":  pct(atual["transacoes"], mom["transacoes"]),
        "var_yoy_transacoes":  pct(atual["transacoes"], yoy["transacoes"]),
        "var_mom_usuarios":    pct(atual["usuarios"],   mom["usuarios"]),
        "var_yoy_usuarios":    pct(atual["usuarios"],   yoy["usuarios"]),
    }


# ── Receita total Web (para slide Orgânico vs Total) ──────────────────────────

def buscar_kpis_separados_sem_filtro(creds, prop_varejo, prop_farma, mes, ano):
    """
    Busca KPIs totais separadamente para Web, App e Farma, sem filtro orgânico.
    Web usa platform=WEB, App usa platform=APP, Farma não usa filtro de plataforma.
    """
    client = _client(creds)

    def fetch_prop(prop_id, start, end, f_plat):
        r = _run(client, prop_id, start, end,
                 ["sessions", "totalUsers", "purchaseRevenue", "engagedSessions"],
                 dimension_filter=f_plat)
        sessoes = _total(r, 0)
        usuarios = _total(r, 1)
        receita = _total(r, 2)
        eng = _total(r, 3)
        tx_eng = (eng / sessoes * 100) if sessoes > 0 else 0.0
        return {
            "sessoes": sessoes,
            "usuarios": usuarios,
            "receita": receita,
            "tx_engajamento": tx_eng,
        }

    atual_s, atual_e = _periodo(mes, ano)
    mom_s, mom_e = _periodo_anterior(mes, ano)
    yoy_s, yoy_e = _mesmo_mes_ano_anterior(mes, ano)

    print(f"  [GA4] KPIs Gerais Separados (Web, App, Farma): {atual_s} -> {atual_e}")

    f_web = _filtro_plataforma("WEB")
    f_app = _filtro_plataforma("APP")

    def build_kpis(prop_id, f_plat):
        atual = fetch_prop(prop_id, atual_s, atual_e, f_plat)
        mom = fetch_prop(prop_id, mom_s, mom_e, f_plat)
        yoy = fetch_prop(prop_id, yoy_s, yoy_e, f_plat)

        def pct(novo, antigo):
            return round((novo - antigo) / antigo * 100, 1) if antigo else None

        return {
            "atual": atual,
            "mom": mom,
            "yoy": yoy,
            "var_mom_sessoes":   pct(atual["sessoes"],        mom["sessoes"]),
            "var_yoy_sessoes":   pct(atual["sessoes"],        yoy["sessoes"]),
            "var_mom_usuarios":  pct(atual["usuarios"],       mom["usuarios"]),
            "var_yoy_usuarios":  pct(atual["usuarios"],       yoy["usuarios"]),
            "var_mom_receita":   pct(atual["receita"],        mom["receita"]),
            "var_yoy_receita":   pct(atual["receita"],        yoy["receita"]),
            "var_mom_tx_eng":    round(atual["tx_engajamento"] - mom["tx_engajamento"], 1),
            "var_yoy_tx_eng":    round(atual["tx_engajamento"] - yoy["tx_engajamento"], 1),
        }

    return {
        "web": build_kpis(prop_varejo, f_web),
        "app": build_kpis(prop_varejo, f_app),
        "farma": build_kpis(prop_farma, None),
    }




def buscar_receita_total_web(creds, property_id, mes, ano):
    """Receita total do site (todos os canais, plataforma WEB)."""
    client = _client(creds)
    start, end = _periodo(mes, ano)
    r = _run(client, property_id, start, end,
             ["purchaseRevenue", "sessions"],
             dimension_filter=_filtro_plataforma("WEB"))
    return {"receita": _total(r, 0), "sessoes": _total(r, 1)}


# ── Série comparativa de receita (índice base 100) ────────────────────────────

def buscar_serie_receita_comparativa(creds, property_id, ano_atual):
    """
    Série mensal de receita orgânica e total (WEB) para gráfico de índice.
    Retorna listas de 12 valores para cada série (ano atual e anterior).
    """
    print(f"  [GA4] Série comparativa de receita {ano_atual-1}/{ano_atual}...")

    org_at  = buscar_serie_mensal(creds, property_id, ano_atual,   "WEB", organico=True)
    tot_at  = buscar_serie_mensal(creds, property_id, ano_atual,   "WEB", organico=False)
    org_ant = buscar_serie_mensal(creds, property_id, ano_atual-1, "WEB", organico=True)
    tot_ant = buscar_serie_mensal(creds, property_id, ano_atual-1, "WEB", organico=False)

    return {
        "organico_atual": [org_at[m]["receita"]  for m in range(1, 13)],
        "total_atual":    [tot_at[m]["receita"]  for m in range(1, 13)],
        "organico_ant":   [org_ant[m]["receita"] for m in range(1, 13)],
        "total_ant":      [tot_ant[m]["receita"] for m in range(1, 13)],
    }
