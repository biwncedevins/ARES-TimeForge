@echo off
setlocal
rem ============================================================
rem  TimeForge — Forensic Timestamp Lab
rem  Build a standalone windowed EXE with PyInstaller.
rem ============================================================
set "ROOT=%~dp0"
cd /d "%ROOT%"

if not exist assets\timeforge.ico (
    echo [*] Generating timeforge.ico from SVG...
    python tools\make_icon.py || exit /b 1
)

echo [*] Building TimeForge.exe ...
python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name TimeForge ^
    --icon assets\timeforge.ico ^
    --add-data "assets;assets" ^
    --hidden-import tzdata ^
    --collect-data tzdata ^
    main.py

if errorlevel 1 (
    echo [X] Build FAILED
    exit /b 1
)

echo [OK] Build complete: %ROOT%dist\TimeForge.exe
endlocal