from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

# A4 landscape @ 96dpi: 297mm x 210mm = 1122px x 794px
_A4_W = 1122
_A4_H = 794


def exportar_html_para_pdf(html_path: str, pdf_path: str) -> str:
    html_file = Path(html_path).resolve()
    pdf_file = Path(pdf_path).resolve()
    pdf_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(
                viewport={"width": _A4_W, "height": _A4_H},
                device_scale_factor=1.5,
            )
            page.goto(html_file.as_uri(), wait_until="networkidle")

            # Aguarda ECharts inicializar e renderizar todos os graficos.
            # Sinaliza via window.__ECHARTS_READY__ quando todos estiverem prontos.
            page.evaluate("""() => {
                window.__ECHARTS_READY__ = false;
                const ids = [
                    'chart-sessoes-web', 'chart-receita-web', 'chart-share-web',
                    'chart-rps-web', 'chart-indice-web', 'chart-impressoes-web',
                    'chart-app-receita', 'chart-impressoes-farma'
                ];
                const checkAll = setInterval(() => {
                    const allReady = ids.every(id => {
                        const el = document.getElementById(id);
                        if (!el) return true;
                        const inst = window.echarts && window.echarts.getInstanceByDom(el);
                        return inst && inst.getOption && Object.keys(inst.getOption()).length > 0;
                    });
                    if (allReady) {
                        clearInterval(checkAll);
                        window.__ECHARTS_READY__ = true;
                    }
                }, 150);
            }""")

            page.wait_for_function("window.__ECHARTS_READY__ === true", timeout=10000)
            # Pausa extra para renderizacao final dos pixels SVG
            page.wait_for_timeout(800)

            page.pdf(
                path=str(pdf_file),
                format="A4",
                landscape=True,
                print_background=True,
                prefer_css_page_size=True,
                margin={"top": "5mm", "right": "5mm", "bottom": "5mm", "left": "5mm"},
            )
            browser.close()
    except Exception as e:
        print("\n" + "=" * 60)
        print(" ERRO AO GERAR O PDF ".center(60, "="))
        print("Ocorreu um erro com o Playwright ao tentar gerar o PDF.")
        print(f"Detalhes: {str(e)}")
        print("-" * 60)
        print("VERIFIQUE SE VOCE EXECUTOU O COMANDO ABAIXO:")
        print("playwright install")
        print("\nCaso nao tenha executado, rode o comando acima no terminal.")
        print("O arquivo HTML ainda foi gerado na pasta output/.")
        print("=" * 60 + "\n")

    return str(pdf_file)
