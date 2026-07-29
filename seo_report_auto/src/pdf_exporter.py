from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright


def exportar_html_para_pdf(html_path: str, pdf_path: str) -> str:
    html_file = Path(html_path).resolve()
    pdf_file = Path(pdf_path).resolve()
    pdf_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1440, "height": 1024}, device_scale_factor=1.5)
            page.goto(html_file.as_uri(), wait_until="networkidle")
            page.wait_for_timeout(3000)
            page.pdf(
                path=str(pdf_file),
                format="A4",
                landscape=True,
                print_background=True,
                prefer_css_page_size=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
            browser.close()
    except Exception as e:
        print("\n" + "="*60)
        print(" ERRO AO GERAR O PDF ".center(60, "="))
        print("Ocorreu um erro com o Playwright ao tentar gerar o PDF.")
        print(f"Detalhes: {str(e)}")
        print("-" * 60)
        print("VERIFIQUE SE VOCÊ EXECUTOU O COMANDO ABAIXO:")
        print("playwright install")
        print("\nCaso não tenha executado, rode o comando acima no terminal.")
        print("O arquivo HTML ainda foi gerado na pasta output/.")
        print("="*60 + "\n")

    return str(pdf_file)
