@echo off
echo ============================================================
echo   Instalador - Gerador de Relatorio SEO Bemol
echo ============================================================
echo.

:: Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale Python 3.10+ e tente novamente.
    pause
    exit /b 1
)

echo [1/3] Instalando dependencias Python...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo [2/4] Criando template Excel de dados manuais...
python criar_template_excel.py

echo.
echo [3/4] Instalando navegadores do Playwright (usados para o PDF)...
playwright install

echo.
echo [4/4] Instalacao concluida!
echo.
echo ============================================================
echo  PROXIMOS PASSOS:
echo.
echo  1. Coloque seu client_secret.json nesta pasta
echo  2. Edite o config.json com seus IDs do GA4 e Search Console
echo  3. Preencha o dados_manuais.xlsx com os dados de IA
echo  4. Execute: python gerar_relatorio.py
echo ============================================================
echo.
pause
