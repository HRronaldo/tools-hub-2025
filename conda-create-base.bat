@echo off
echo Creating clean Python 3.10.19 environment...
conda create -n toolhub-env python=3.10.19 -y

echo.
echo Installing packages from requirements.txt (Tsinghua mirror)...
call conda activate toolhub-env
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ========================================
echo Environment ready! You can now run run.bat
echo ========================================
pause
