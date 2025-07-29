@echo off
cd /d "C:\Users\willl\Documents\O-ni\O-ni"
echo Starting O-ni bot...
pause
echo Installing requirements from requirements.txt...

:: Check if Python is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: Upgrade pip (optional but recommended)
python -m pip install --upgrade pip

:: Install requirements
python -m pip install -r requirements.txt
pause
cls
:: Done
echo.
echo All requirements installed.

ollama serve
echo Ollama started

python -m bot