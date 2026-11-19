@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" run.py --open %*
) else (
    python run.py --open %*
)
if errorlevel 1 pause
