#!/usr/bin/env bash
# Exit on error
set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (Chromium only) to a local directory for persistence
# Using dirname $0 to ensure it's always inside the backend folder
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PLAYWRIGHT_BROWSERS_PATH="$SCRIPT_DIR/pw-browsers"
echo "Installing browsers to $PLAYWRIGHT_BROWSERS_PATH"
playwright install chromium