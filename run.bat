@echo off
:: console encoding to UTF-8
chcp 65001 > nul

title Launching the AI Discord Bot

echo ========================================
echo   Checking and installing dependencies...
echo ========================================
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ========================================
echo   Launching the interface...
echo ========================================
python GUI.py

if %errorlevel% neq 0 (
    echo.
    echo [!] An error occurred while executing the script.
    pause
)