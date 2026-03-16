#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r backend/requirements.txt

# Export the local Playwright browsers path so the app finds them
# This MUST match the path in backend/build.sh
export PLAYWRIGHT_BROWSERS_PATH=$(pwd)/backend/pw-browsers
echo "STARTUP: Using PLAYWRIGHT_BROWSERS_PATH=$PLAYWRIGHT_BROWSERS_PATH"

# Verify if the browser exists to give better logs
if [ -d "$PLAYWRIGHT_BROWSERS_PATH" ]; then
    echo "STARTUP: Playwright browsers directory found."
    ls -R "$PLAYWRIGHT_BROWSERS_PATH" | head -n 5
else
    echo "ERROR: Playwright browsers directory NOT FOUND at $PLAYWRIGHT_BROWSERS_PATH"
fi

# Run the application
python backend/run.py
