# Use official Python 3.11 slim image
FROM python:3.11-slim-bookworm

# Set user to root to install system dependencies
USER root

# Install system dependencies required for Playwright
# These are the full dependencies for Chromium on Debian Bookworm
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    libnss3 \
    libnspr4 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libx11-xcb1 \
    fonts-liberation \
    libatspi2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file first to leverage Docker cache
# Assuming backend/requirements.txt exists relative to build context
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium only)
RUN playwright install --with-deps chromium

# Copy the backend code into the container
# Copying backend/ contents into /app/ so that run.py is at /app/run.py
COPY backend/ .

# Expose the port the app runs on
ENV PORT=10000
EXPOSE 10000

# Command to run the application
# Using python run.py which invokes uvicorn
CMD ["python", "run.py"]
