#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r backend/requirements.txt

# Export the local Playwright browsers path so the app finds them
# (They are installed here by backend/build.sh)
export PLAYWRIGHT_BROWSERS_PATH=$(pwd)/backend/pw-browsers
echo "STARTUP: Using PLAYWRIGHT_BROWSERS_PATH=$PLAYWRIGHT_BROWSERS_PATH"

# Run the application
python backend/run.py
