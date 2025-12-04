@echo off
cd /d D:\programs\tools-hub-2025

call conda activate toolhub-env
if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo ERROR: conda environment toolhub-env not found
    echo Please run conda-create-base.bat first
    echo ============================================
    echo.
    pause
    exit /b 1
)

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
