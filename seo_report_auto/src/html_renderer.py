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
