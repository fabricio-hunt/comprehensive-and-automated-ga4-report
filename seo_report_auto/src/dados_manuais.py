"""
Lê dados manuais do Excel (dados_manuais.xlsx).
Esses dados não têm API disponível:
- Visibilidade na IA (Semrush/BrightEdge): menções, citações, páginas citadas, score
- Série histórica de IA
"""

import pandas as pd
from pathlib import Path


def carregar_dados_ia(excel_path: str) -> dict:
    """
    Lê a aba 'IA_Varejo' e 'IA_Farma' do Excel de dados manuais.
    Retorna dicionário com dados de visibilidade na IA para Varejo e Farma.
    """
    path = Path(excel_path)
    if not path.exists():
        print(f"[Aviso] Arquivo de dados manuais não encontrado: {excel_path}")
        return _dados_ia_vazio()

    try:
        # ---- Varejo ----
        df_varejo = pd.read_excel(path, sheet_name="IA_Varejo", header=0)
        varejo = _parse_ia_sheet(df_varejo)

        # ---- Farma ----
        df_farma = pd.read_excel(path, sheet_name="IA_Farma", header=0)
        farma = _parse_ia_sheet(df_farma)

        # ---- Série histórica ----
        df_serie_v = pd.read_excel(path, sheet_name="IA_Serie_Varejo", header=0)
        df_serie_f = pd.read_excel(path, sheet_name="IA_Serie_Farma", header=0)

        return {
            "varejo": varejo,
            "farma": farma,
            "serie_varejo": _parse_serie(df_serie_v),
            "serie_farma": _parse_serie(df_serie_f),
        }

    except Exception as e:
        print(f"[Aviso] Erro ao ler dados manuais: {e}")
        return _dados_ia_vazio()


def _parse_ia_sheet(df: pd.DataFrame) -> dict:
    """
    Espera colunas: Métrica | Atual | Anterior | Variação(%)
    Linhas: Menções, Citações, Páginas_citadas, Score
    """
    result = {}
    try:
        for _, row in df.iterrows():
            metrica = str(row.iloc[0]).strip().lower().replace(" ", "_")
            result[metrica] = {
                "atual": _safe_num(row.iloc[1]),
                "anterior": _safe_num(row.iloc[2]),
                "variacao_pct": _safe_num(row.iloc[3]),
            }
    except Exception as e:
        print(f"[Aviso] Erro ao parsear aba IA: {e}")
    return result


def _parse_serie(df: pd.DataFrame) -> dict:
    """
    Espera colunas: Mês | Menções | Citações | Páginas_citadas
    Retorna listas para uso nos gráficos.
    """
    try:
        return {
            "labels": df.iloc[:, 0].astype(str).tolist(),
            "mencoes": df.iloc[:, 1].fillna(0).tolist(),
            "citacoes": df.iloc[:, 2].fillna(0).tolist(),
            "paginas_citadas": df.iloc[:, 3].fillna(0).tolist(),
        }
    except Exception as e:
        print(f"[Aviso] Erro ao parsear série IA: {e}")
        return {"labels": [], "mencoes": [], "citacoes": [], "paginas_citadas": []}


def _safe_num(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def _dados_ia_vazio() -> dict:
    """Retorna estrutura vazia para não quebrar o PDF se o Excel não existir."""
    kpis_vazio = {
        "mencoes": {"atual": 0, "anterior": 0, "variacao_pct": 0},
        "citacoes": {"atual": 0, "anterior": 0, "variacao_pct": 0},
        "paginas_citadas": {"atual": 0, "anterior": 0, "variacao_pct": 0},
        "score": {"atual": 0, "anterior": 0, "variacao_pct": 0},
    }
    serie_vazio = {"labels": [], "mencoes": [], "citacoes": [], "paginas_citadas": []}
    return {
        "varejo": kpis_vazio,
        "farma": kpis_vazio,
        "serie_varejo": serie_vazio,
        "serie_farma": serie_vazio,
    }
