from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
ASSETS_DIR = BASE_DIR / "assets"


def _copiar_assets_para_output(output_dir: Path) -> None:
    """
    Garante que os arquivos referenciados no HTML existam em output/assets.
    O template usa caminhos relativos como assets/report/report.css.
    """
    destino_assets = output_dir / "assets"
    destino_assets.mkdir(parents=True, exist_ok=True)

    # Copia CSS/JS do relatório
    origem_report = ASSETS_DIR / "report"
    if origem_report.exists():
        shutil.copytree(origem_report, destino_assets / "report", dirs_exist_ok=True)

    # Copia logos usadas pelo template (se existirem)
    for nome_logo in ("logo_bemol.png", "logo_farma.png"):
        origem_logo = ASSETS_DIR / nome_logo
        if origem_logo.exists():
            shutil.copy2(origem_logo, destino_assets / nome_logo)


def renderizar_relatorio_html(payload: dict[str, Any], output_html_path: str) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    css_path = ASSETS_DIR / "report" / "report.css"
    inline_css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    
    js_path = ASSETS_DIR / "report" / "report.js"
    inline_js = js_path.read_text(encoding="utf-8") if js_path.exists() else ""

    template = env.get_template("report.html")
    html = template.render(
        payload=payload,
        charts_json=json.dumps(payload.get("charts", {}), ensure_ascii=False),
        inline_css=inline_css,
        inline_js=inline_js,
    )

    output_path = Path(output_html_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _copiar_assets_para_output(output_path.parent)
    output_path.write_text(html, encoding="utf-8")
    return str(output_path)


def gerar_indice_html(output_dir: Path) -> str:
    """
    Gera a página index.html dentro de output/ listando todos os relatórios disponíveis.
    Assim, quando hospedado na Vercel, o link principal exibe um portal limpo com todos os meses.
    """
    relatorios = sorted(
        [f for f in output_dir.glob("Relatorio_SEO_*.html")],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    cards_html = ""
    for f in relatorios:
        nome_exibicao = f.stem.replace("Relatorio_SEO_", "").replace("_", " / ")
        cards_html += f"""
        <a href="{f.name}" class="report-card">
          <div class="card-icon">📊</div>
          <div class="card-info">
            <h3>Relatório SEO</h3>
            <p>{nome_exibicao}</p>
          </div>
          <div class="card-arrow">→</div>
        </a>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bemol — Central de Relatórios SEO & Search</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 0;
      font-family: 'Inter', sans-serif;
      background: #f2f4f7;
      color: #1a2332;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}
    .header {{
      background: #ffffff;
      border-bottom: 1px solid #e2e8f0;
      padding: 24px 40px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }}
    .header-left h1 {{
      margin: 0;
      font-size: 22px;
      font-weight: 800;
      color: #1570d8;
      font-family: 'Nunito', sans-serif;
    }}
    .header-left p {{
      margin: 4px 0 0;
      font-size: 13px;
      color: #64748b;
    }}
    .container {{
      max-width: 1000px;
      margin: 48px auto;
      padding: 0 24px;
      width: 100%;
    }}
    .section-title {{
      font-size: 16px;
      font-weight: 700;
      color: #475569;
      margin-bottom: 20px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;
    }}
    .report-card {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      padding: 24px;
      text-decoration: none;
      color: inherit;
      display: flex;
      align-items: center;
      gap: 16px;
      transition: all 0.2s ease;
      box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }}
    .report-card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 10px 25px rgba(21, 112, 216, 0.12);
      border-color: #3b82f6;
    }}
    .card-icon {{
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: #e0f2fe;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
    }}
    .card-info h3 {{
      margin: 0;
      font-size: 15px;
      font-weight: 700;
      color: #1e293b;
    }}
    .card-info p {{
      margin: 4px 0 0;
      font-size: 14px;
      font-weight: 600;
      color: #1570d8;
    }}
    .card-arrow {{
      margin-left: auto;
      color: #94a3b8;
      font-size: 18px;
      font-weight: 700;
    }}
  </style>
</head>
<body>
  <div class="header">
    <div class="header-left">
      <h1>Bemol | Performance SEO & Search</h1>
      <p>Portal Executivo de Acompanhamento Mensal | Varejo, Farma & App</p>
    </div>
  </div>
  <div class="container">
    <div class="section-title">Relatórios Mensais Disponíveis</div>
    <div class="grid">
      {cards_html}
    </div>
  </div>
</body>
</html>"""
    index_path = output_dir / "index.html"
    index_path.write_text(html_content, encoding="utf-8")
    nojekyll_path = output_dir / ".nojekyll"
    nojekyll_path.touch(exist_ok=True)
    return str(index_path)

