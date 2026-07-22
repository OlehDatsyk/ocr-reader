@echo off
setlocal enabledelayedexpansion
title OCR Reader - Startup
cd /d "%~dp0"

echo ============================================================
echo   OCR Reader - Startup
echo ============================================================
echo.

REM --- Step 1: Verify Python is installed -------------------------------
echo [1/6] Checking for Python...
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: Python was not found on your PATH.
    echo Please install Python 3.12 or newer from https://www.python.org/downloads/
    echo IMPORTANT: during installation, check "Add python.exe to PATH".
    echo.
    pause
    exit /b 1
)
python --version
echo Python found.
echo.

REM --- Step 2: Create the virtual environment if it does not exist ------
echo [2/6] Checking for virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment in .\venv ...
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to create the virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)
echo.

REM --- Step 3: Activate the virtual environment --------------------------
echo [3/6] Activating virtual environment...
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo.
    echo ERROR: Failed to activate the virtual environment.
    pause
    exit /b 1
)
echo Virtual environment activated.
echo.

REM --- Step 4: Install dependencies --------------------------------------
echo [4/6] Installing dependencies (this may take a minute the first time)...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies. Check your internet connection.
    pause
    exit /b 1
)
echo Dependencies installed.
echo.

REM --- Step 5: Verify the .env file ---------------------------------------
echo [5/6] Checking for .env file...
if not exist ".env" (
    echo No .env file found. Creating one from .env.example ...
    copy /y ".env.example" ".env" >nul
    echo.
    echo ============================================================
    echo   ACTION REQUIRED
    echo   A new .env file was created. Open it in a text editor and
    echo   set OPENAI_API_KEY to your real OpenAI API key, then run
    echo   this script again.
    echo ============================================================
    echo.
    pause
    exit /b 0
)

findstr /C:"OPENAI_API_KEY=sk-your-api-key-here" ".env" >nul
if not errorlevel 1 (
    echo.
    echo ============================================================
    echo   ACTION REQUIRED
    echo   .env still contains the placeholder API key.
    echo   Open .env in a text editor and set OPENAI_API_KEY to your
    echo   real OpenAI API key, then run this script again.
    echo ============================================================
    echo.
    pause
    exit /b 0
)
echo .env file found.
echo.

REM --- Step 6: Launch the application -------------------------------------
echo [6/6] Starting OCR Reader...
echo The app will be available at http://127.0.0.1:8000
echo Press CTRL+C in this window to stop the server.
echo.
python main.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo   The application exited with an error. See the messages
    echo   above and the logs\app.log file for details.
    echo ============================================================
    pause
    exit /b 1
)

pause
