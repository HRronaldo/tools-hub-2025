@echo off
cd /d D:\programs\tools-hub-2025

echo Checking/Downloading nssm (only first time)...
if not exist nssm.exe (
    echo Downloading nssm 2.24...
    powershell -Command "Invoke-WebRequest -Uri https://nssm.cc/release/nssm-2.24.zip -OutFile nssm.zip" -Wait
    powershell -Command "Expand-Archive -Force nssm.zip ." -Wait
    copy nssm-2.24\win64\nssm.exe . >nul
    rd /s /q nssm-2.24
    del nssm.zip 2>nul
    echo nssm ready
)

echo.
echo Checking conda environment toolhub-env...
call conda activate toolhub-env 2>nul
if %errorlevel% neq 0 (
    echo.
    echo =================================================
    echo ERROR: toolhub-env not found on this machine!
    echo Please run conda-create-base.bat first
    echo =================================================
    echo.
    pause
    exit /b 1
)

echo Installing/Updating Windows service [ToolHub]...
nssm install ToolHub "%CONDA_PREFIX%\python.exe" "D:\programs\tools-hub-2025\main.py" >nul 2>&1
nssm set ToolHub AppDirectory "D:\programs\tools-hub-2025" >nul
nssm set ToolHub Start SERVICE_AUTO_START >nul

echo Starting service...
nssm start ToolHub >nul 2>&1

echo.
echo ========================================
echo ToolHub service started and set to auto-start
echo Access: http://YOUR_NAS_IP:8000
echo Stop:   nssm stop ToolHub
echo Remove: nssm remove ToolHub confirm
echo ========================================
echo.
pause
