#!/usr/bin/env bash
# Exit on error
set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (Chromium only) to a local directory for persistence
export PLAYWRIGHT_BROWSERS_PATH=$(pwd)/pw-browsers
echo "Installing browsers to $PLAYWRIGHT_BROWSERS_PATH"
#playwright install chromium
python -m playwright install --with-deps chromium