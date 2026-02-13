#!/usr/bin/env bash
# Exit on error
set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install Playwright OS dependencies (Critical for Render)
playwright install-deps chromium

# Install Playwright browsers (Chromium only)
playwright install chromium
