@echo off
setlocal
rem ============================================================
rem  TimeForge — run from source with Python.
rem ============================================================
set "ROOT=%~dp0"
cd /d "%ROOT%"
python main.py
endlocal