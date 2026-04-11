#!/usr/bin/env bash
# ============================================================================
# run.sh — One-command local startup for PMPML Saarthi
#
# What it does:
#   1. Creates a Python virtual environment (if needed)
#   2. Installs backend dependencies
#   3. (Optionally) downloads the spaCy English model
#   4. Seeds Firebase with sample data (if credentials are configured)
#   5. Starts the FastAPI backend on port 8000
#   6. Prints instructions for starting the Expo mobile app
# ============================================================================
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
MOBILE_DIR="$ROOT_DIR/mobile"
VENV_DIR="$BACKEND_DIR/.venv"

echo "============================================"
echo "  PMPML Saarthi — Local Setup"
echo "============================================"
echo ""

# ------------------------------------------------------------------
# 1. Python virtual environment
# ------------------------------------------------------------------
if [ ! -d "$VENV_DIR" ]; then
  echo "▸ Creating Python virtual environment…"
  python3 -m venv "$VENV_DIR"
fi

echo "▸ Activating virtual environment…"
source "$VENV_DIR/bin/activate" 2>/dev/null || source "$VENV_DIR/Scripts/activate"

# ------------------------------------------------------------------
# 2. Install backend dependencies
# ------------------------------------------------------------------
echo "▸ Installing backend dependencies…"
pip install --quiet --upgrade pip
pip install --quiet -r "$BACKEND_DIR/requirements.txt"

# ------------------------------------------------------------------
# 3. (Optional) Download spaCy model
# ------------------------------------------------------------------
if python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
  echo "▸ spaCy model already installed."
else
  echo "▸ Downloading spaCy en_core_web_sm model (optional, ~12 MB)…"
  python -m spacy download en_core_web_sm || echo "  ⚠ skipped (regex extractor will be used instead)"
fi

# ------------------------------------------------------------------
# 4. Seed Firebase (only if credentials exist)
# ------------------------------------------------------------------
if [ -f "$ROOT_DIR/.env" ]; then
  export $(grep -v '^#' "$ROOT_DIR/.env" | xargs)
fi

if [ -n "$FIREBASE_CREDENTIALS_PATH" ] && [ -f "$FIREBASE_CREDENTIALS_PATH" ]; then
  echo "▸ Seeding Firestore with sample PMPML data…"
  python "$ROOT_DIR/firebase/seed_data.py"
else
  echo "▸ Skipping Firebase seed (no credentials found)."
  echo "  The backend will use built-in fallback data."
fi

# ------------------------------------------------------------------
# 5. Start FastAPI
# ------------------------------------------------------------------
echo ""
echo "============================================"
echo "  Starting FastAPI backend on :8000"
echo "============================================"
echo ""
cd "$BACKEND_DIR"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "▸ Backend PID: $BACKEND_PID"

# ------------------------------------------------------------------
# 6. Print Expo instructions
# ------------------------------------------------------------------
echo ""
echo "============================================"
echo "  Mobile App (Expo) — Manual Steps"
echo "============================================"
echo ""
echo "  In a new terminal:"
echo ""
echo "    cd $MOBILE_DIR"
echo "    npm install"
echo "    npx expo start"
echo ""
echo "  Then scan the QR code with Expo Go,"
echo "  or press 'a' for Android / 'i' for iOS."
echo ""
echo "  To point the mobile app to this backend:"
echo "    - Android emulator uses http://10.0.2.2:8000"
echo "    - iOS simulator uses http://localhost:8000"
echo "    - Physical device: use your machine's LAN IP"
echo ""
echo "============================================"
echo "  Backend running — press Ctrl+C to stop"
echo "============================================"

# Wait for backend to finish (Ctrl+C exits)
wait $BACKEND_PID
