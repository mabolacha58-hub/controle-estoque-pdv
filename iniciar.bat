@echo off
cd /d "%~dp0"
title Controle de Estoque - PDV/ERP
chcp 65001 >nul
echo.
echo   ===============================================
echo     CONTROLE DE ESTOQUE - SISTEMA PDV/ERP
echo   ===============================================
echo.
echo   1 - Modo Desktop Nativo (Electron) *
echo   2 - Modo Desktop Clássico (pywebview)
echo   3 - Modo Web Local (Navegador)
echo   4 - Sair
echo.
echo   * Recomendado - visual profissional, menus,
echo     notificações nativas, impressão direta
echo.
set /p op="Escolha: "
if "%op%"=="1" (
    if exist "node_modules\.bin\electron.cmd" (
        start "" /MIN /B npx electron .
    ) else (
        echo.
        echo   A instalar dependências Electron (primeira execução)...
        call npm install
        start "" /MIN /B npx electron .
    )
)
if "%op%"=="2" start "" /MIN pythonw desktop_launcher.py
if "%op%"=="3" start /B python app.py & timeout /t 2 >nul & start http://localhost:5000
exit
