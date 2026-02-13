# Docker Migration Guide for InfiniteBZ

## 🚨 CRITICAL: Force Docker Runtime 🚨

Because Render previously detected this project as Python, it might stick to the Python environment even with a Dockerfile present.

**YOU MUST DELETE THE OLD SERVICE TO FIX THIS.**

## 1. Steps to Deploy (The "Nuclear" Option)

### Step 1: Delete Old Service
1. Go to your **Render Dashboard**.
2. Click on your **Backend Service** (e.g., `project1-kmm5`).
3. Scroll to the bottom of **Settings**.
4. Click **Delete Web Service**.
   - *Don't worry, your database is safe (it's a separate service).*

### Step 2: Create New Docker Service
1. Click **New +** -> **Web Service**.
2. Connect your GitHub repository (`project1`).
3. **CRITICAL STEP: Select Runtime**
   - Render might auto-detect files.
   - **MAKE SURE "Docker" IS SELECTED.** (Do NOT select "Python 3").
4. **Environment Variables**:
   - Add `DATABASE_URL`: (Copy the internal connection string from your Postgres service).
   - Add `PORT`: `10000`.
5. Click **Create Web Service**.

## 2. Why this is necessary
The error `Failed to install browsers` happens because the Python runtime on Render blocks system-level installations (like `apt-get`). Only the **Docker** runtime allows us to install the necessary libraries for Playwright.

## 3. Verification
Watch the deployment logs. You should see:
- `[+] Building ...`
- `RUN apt-get update && apt-get install -y ...` (Installing system deps)
- `RUN playwright install --with-deps chromium` (Installing Chrome)

Once deployed, your scraper will work perfectly.
