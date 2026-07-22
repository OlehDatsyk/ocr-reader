#!/usr/bin/env bash
# =============================================================================
# OCR Reader - macOS startup script
# Double-click this file in Finder to set up and launch OCR Reader.
# =============================================================================
set -u
cd "$(dirname "$0")"

echo "============================================================"
echo "  OCR Reader - Startup"
echo "============================================================"
echo

fail() {
    echo
    echo "ERROR: $1"
    echo
    echo "Press Return to close this window..."
    read -r _
    exit 1
}

# --- Step 1: Verify Python is installed ------------------------------------
echo "[1/6] Checking for Python 3..."
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
fi

if [ -z "$PYTHON_BIN" ]; then
    fail "Python 3 was not found. Install it from https://www.python.org/downloads/ (or 'brew install python') and run this script again."
fi
"$PYTHON_BIN" --version
echo "Python found."
echo

# --- Step 2: Create the virtual environment if it does not exist -----------
echo "[2/6] Checking for virtual environment..."
if [ ! -f "venv/bin/activate" ]; then
    echo "Creating virtual environment in ./venv ..."
    "$PYTHON_BIN" -m venv venv || fail "Failed to create the virtual environment."
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi
echo

# --- Step 3: Activate the virtual environment -------------------------------
echo "[3/6] Activating virtual environment..."
# shellcheck disable=SC1091
source "venv/bin/activate" || fail "Failed to activate the virtual environment."
echo "Virtual environment activated."
echo

# --- Step 4: Install dependencies --------------------------------------------
echo "[4/6] Installing dependencies (this may take a minute the first time)..."
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt || fail "Failed to install dependencies. Check your internet connection."
echo "Dependencies installed."
echo

# --- Step 5: Verify the .env file ---------------------------------------------
echo "[5/6] Checking for .env file..."
if [ ! -f ".env" ]; then
    echo "No .env file found. Creating one from .env.example ..."
    cp ".env.example" ".env"
    echo
    echo "============================================================"
    echo "  ACTION REQUIRED"
    echo "  A new .env file was created. Open it in a text editor and"
    echo "  set OPENAI_API_KEY to your real OpenAI API key, then run"
    echo "  this script again."
    echo "============================================================"
    echo
    echo "Press Return to close this window..."
    read -r _
    exit 0
fi

if grep -q "OPENAI_API_KEY=sk-your-api-key-here" ".env"; then
    echo
    echo "============================================================"
    echo "  ACTION REQUIRED"
    echo "  .env still contains the placeholder API key."
    echo "  Open .env in a text editor and set OPENAI_API_KEY to your"
    echo "  real OpenAI API key, then run this script again."
    echo "============================================================"
    echo
    echo "Press Return to close this window..."
    read -r _
    exit 0
fi
echo ".env file found."
echo

# --- Step 6: Launch the application --------------------------------------------
echo "[6/6] Starting OCR Reader..."
echo "The app will be available at http://127.0.0.1:8000"
echo "Press CTRL+C in this window to stop the server."
echo
python main.py

status=$?
if [ $status -ne 0 ]; then
    fail "The application exited with an error. See the messages above and the logs/app.log file for details."
fi

echo "Press Return to close this window..."
read -r _
