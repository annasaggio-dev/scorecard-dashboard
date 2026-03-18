#!/bin/bash
# Scorecard Dashboard launcher
# Run this script to start the dashboard.
# It will guide you through authorization if needed.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "====================================="
echo "  Scorecard Dashboard"
echo "====================================="

if [ ! -f "token.json" ]; then
  echo ""
  echo "  First-time setup: authorizing with Google..."
  echo ""
  python3 setup_auth.py
  if [ $? -ne 0 ]; then
    echo "Authorization failed. Please try again."
    exit 1
  fi
fi

echo ""
echo "  Starting server at http://localhost:5000"
echo "  Press Ctrl+C to stop."
echo ""
python3 app.py
