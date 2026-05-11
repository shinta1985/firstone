@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo eBay Listing Task Navigator - Windows
echo ========================================
echo.

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Creating Python virtual environment...
  py -3.13 -m venv .venv || py -3 -m venv .venv || python -m venv .venv
  if errorlevel 1 (
    echo.
    echo Failed to create virtual environment.
    echo Please install Python 3.13 or Python 3 from https://www.python.org/downloads/windows/
    pause
    exit /b 1
  )
) else (
  echo [1/4] Existing virtual environment found.
)

echo [2/4] Activating virtual environment...
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo Failed to activate virtual environment.
  pause
  exit /b 1
)

echo [3/4] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Dependency installation failed. Check your internet connection and Python installation.
  pause
  exit /b 1
)

echo [4/4] Starting Streamlit...
echo When the browser opens, use the local app page. Press Ctrl+C here to stop the app.
echo.
streamlit run app.py

pause
