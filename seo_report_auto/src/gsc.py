"""
Busca dados da Google Search Console via API.
Retorna impressões, CTR, posição média, top páginas e top queries.
"""

from datetime import date
from dateutil.relativedelta import relativedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def _service(creds: Credentials):
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def _periodo(mes: int, ano: int):
    inicio = date(ano, mes, 1)
    from datetime import timedelta
    fim = (inicio + relativedelta(months=1)) - timedelta(days=1)
    return inicio.strftime("%Y-%m-%d"), fim.strftime("%Y-%m-%d")


def _periodo_anterior(mes: int, ano: int):
    ref = date(ano, mes, 1) - relativedelta(months=1)
    return _periodo(ref.month, ref.year)


def _mesmo_mes_ano_anterior(mes: int, ano: int):
    return _periodo(mes, ano - 1)


def _query(service, site_url, start, end, dimensions=None, row_limit=10,
           dimension_filter_groups=None):
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": dimensions or [],
        "rowLimit": row_limit,
        "startRow": 0,
    }
    if dimension_filter_groups:
        body["dimensionFilterGroups"] = dimension_filter_groups

    resp = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
    return resp.get("rows", [])


def buscar_kpis_gsc(creds, site_url, mes, ano):
    """
    Retorna impressões orgânicas, posição média e CTR.
    Inclui variações MoM e YoY.
    """
    svc = _service(creds)

    atual_start, atual_end = _periodo(mes, ano)
    mom_start, mom_end = _periodo_anterior(mes, ano)
    yoy_start, yoy_end = _mesmo_mes_ano_anterior(mes, ano)

    print(f"  [GSC] Buscando KPIs: {atual_start} -> {atual_end} para {site_url}")

    def fetch(start, end):
        rows = _query(svc, site_url, start, end, dimensions=[], row_limit=1)
        if not rows:
            return {"impressoes": 0, "cliques": 0, "ctr": 0, "posicao": 0}
        r = rows[0]
        return {
            "impressoes": r.get("impressions", 0),
            "cliques": r.get("clicks", 0),
            "ctr": round(r.get("ctr", 0) * 100, 1),
            "posicao": round(r.get("position", 0), 1),
        }

    atual = fetch(atual_start, atual_end)
    mom = fetch(mom_start, mom_end)
    yoy = fetch(yoy_start, yoy_end)

    def pct(novo, antigo):
        if antigo == 0:
            return None
        return round((novo - antigo) / antigo * 100, 1)

    return {
        "atual": atual,
        "mom": mom,
        "yoy": yoy,
        "var_mom_impressoes": pct(atual["impressoes"], mom["impressoes"]),
        "var_yoy_impressoes": pct(atual["impressoes"], yoy["impressoes"]),
        "var_mom_posicao": round(atual["posicao"] - mom["posicao"], 1),
    }


def buscar_serie_impressoes(creds, site_url, mes_atual, ano_atual):
    """
    Série mensal de impressões dos últimos 7 meses (para o gráfico de evolução).
    """
    svc = _service(creds)
    serie = []
    labels = []

    ref = date(ano_atual, mes_atual, 1) - relativedelta(months=6)
    for _ in range(7):
        start, end = _periodo(ref.month, ref.year)
        rows = _query(svc, site_url, start, end, dimensions=[], row_limit=1)
        impressoes = rows[0].get("impressions", 0) if rows else 0
        serie.append(impressoes)
        labels.append(f"{ref.strftime('%b/%y')}")
        ref = ref + relativedelta(months=1)

    return {"labels": labels, "impressoes": serie}


def buscar_top_paginas(creds, site_url, mes, ano, top_n=10):
    """Top N páginas por impressões, com tipo inferido da URL e filtros de páginas internas/empréstimos."""
    svc = _service(creds)
    start, end = _periodo(mes, ano)
    print(f"  [GSC] Buscando top páginas...")

    termos_excluir_paginas = [
        "emprestimo", "empréstimo", "account", "contabemol", "atendimento",
        "renegociacao", "renegociação", "nossas-lojas", "login", "carrinho",
        "cart", "checkout", "pedido", "institucional", "central-de-atendimento",
        "ajuda", "trabalhe-conosco", "quem-somos", "faq", "termos",
        "privacidade", "vendedores", "listas", "manaus", "exames"
    ]

    rows = _query(svc, site_url, start, end, dimensions=["page"], row_limit=500)
    resultado = []
    for r in rows:
        url_raw = r["keys"][0]
        pagina = url_raw.replace(site_url.rstrip("/"), "")
        if pagina in ("/", "", site_url) or any(t in pagina.lower() for t in termos_excluir_paginas):
            continue
        tipo = _inferir_tipo(pagina)
        resultado.append({
            "pagina": pagina,
            "impressoes": int(r.get("impressions", 0)),
            "tipo": tipo,
        })

    resultado.sort(key=lambda x: x["impressoes"], reverse=True)
    return resultado[:top_n]


def buscar_top_queries_sem_marca(creds, site_url, mes, ano, top_n=10,
                                  termos_marca=None):
    """Top N queries por impressões, excluindo termos de marca, empréstimos e termos internos."""
    svc = _service(creds)
    start, end = _periodo(mes, ano)
    print(f"  [GSC] Buscando top queries sem marca...")

    termos_marca_padrao = [
        "bemol", "bemolfarma", "bemol farma", "benol", "bmol", "bemil",
        "bemo", "beol", "ertc", "vemol", "baumon", "brmol", "belmo", "bomel",
        "bémol", "bermol", "bwmol", "demol", "nemol", "beml", "bemool",
        "bemom", "bemul", "bemo;", "bemot", "bemok", "bemop", "bemou",
        "bemoh", "bemon", "bemoz", "bemos", "bemoo", "belmol", "biomol",
        "bemal", "beemol", "bemoll", "bemmo", "bemm", "benmol", "bremol",
        "benil", "bemo l", "be mol", "b emol", "bm", "emol", "sim"
    ]
    termos_financeiros_excluir = [
        "emprest", "emprést", "renegocia", "credito", "crédito", "carne",
        "carnê", "fatura", "contabemol", "conta bemol", "saque", "dinheiro",
        "saldo", "cartao", "cartão", "200 reais", "100 reais", "300 reais",
        "500 reais", "reais urgente", "reais agora", "emprestado", "parcela",
        "financia", "divida", "dívida", "pagar", "pagamento", "product",
        "http", "www", ".com", "incesto", "sex", "camisinha", "porno", "xxx"
    ]
    termos_excluir = list(set((termos_marca or []) + termos_marca_padrao + termos_financeiros_excluir))

    rows = _query(svc, site_url, start, end, dimensions=["query"], row_limit=500)

    filtradas = []
    for r in rows:
        query = r["keys"][0].lower()
        if not any(m in query for m in termos_excluir):
            filtradas.append({
                "consulta": r["keys"][0],
                "impressoes": int(r.get("impressions", 0)),
            })

    filtradas.sort(key=lambda x: x["impressoes"], reverse=True)
    return filtradas[:top_n]


def buscar_total_keywords(creds, site_url, mes, ano):
    """Número total de palavras-chave ativas (queries com pelo menos 1 impressão)."""
    svc = _service(creds)
    start, end = _periodo(mes, ano)
    print(f"  [GSC] Contando palavras-chave ativas...")

    # Busca em lotes para contar total
    total = 0
    start_row = 0
    while True:
        body = {
            "startDate": start,
            "endDate": end,
            "dimensions": ["query"],
            "rowLimit": 25000,
            "startRow": start_row,
        }
        resp = svc.searchanalytics().query(siteUrl=site_url, body=body).execute()
        rows = resp.get("rows", [])
        total += len(rows)
        if len(rows) < 25000:
            break
        start_row += 25000

    return total


def _inferir_tipo(url: str) -> str:
    """Infere o tipo de página pela estrutura da URL."""
    if url.endswith("/p") or "/p/" in url or url.count("/") >= 3:
        return "produto"
    if url == "/" or url == "":
        return "home"
    return "categoria"
