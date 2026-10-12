@echo off
cd /d "%~dp0"
start "" /B python app.py
timeout /t 2 >nul
start http://localhost:5000
exit
