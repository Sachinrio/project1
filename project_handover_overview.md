# Infinite BZ - Project Handover & Understanding

**Date:** Feb 02, 2026
**Version:** 1.2 (Merged with Team + Pollinations AI)

## 1. Project Overview
**Infinite BZ** is a full-stack event management platform that aggregates events from external sources (Eventbrite, Meetup) and provides a SaaS platform for event organizers to manage tickets, registrations, and check-ins.

*   **Core Goals**: Aggregation (Consumer side) + Event Hosting (Business side).
*   **Current State**: "Phase 2" completed (Team Merge, Ticketing System, AI Images).
*   **New Feature**: "AI Magic Build" - Enhanced with **Pollinations.ai** for cover images and strict schema validation.

## 2. Quick Start Guide
To get up and running immediately on a new machine or account:

### Prerequisites
*   Docker & Docker Compose installed.
*   Git installed.
*   **Groq API Key**: Required for AI features.

### Installation
1.  **Clone the Repository**:
    ```bash
    git clone <repository_url>
    cd business_develop
    ```

2.  **Environment Setup**:
    Copy the example environment file to create your local `.env`:
    ```bash
    cp .env.example Infinite_BZ/backend/.env
    ```
    *   Update `MAIL_USERNAME` and `MAIL_PASSWORD` for emails.
    *   **CRITICAL**: Add `GROQ_API_KEY` to `.env` for AI event generation.

3.  **Run the Request Services**:
    Since this is a monorepo, you only need to run the `Infinite_BZ` services:
    ```bash
    # Run Locally (Recommended for dev)
    cd Infinite_BZ/backend && uvicorn app.api.routes:router --reload --port 8000
    cd Infinite_BZ/frontend && npm run dev
    ```

4.  **Access the Application**:
    *   **Frontend**: [http://localhost:5174](http://localhost:5174) (Port may vary, check npm output)
    *   **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 3. Architecture & Tech Stack

### Frontend (`Infinite_BZ/frontend`)
*   **Framework**: React (Vite)
*   **Styling**: Tailwind CSS
*   **State/Routing**: React Router, Context API
*   **Key Components**:
    *   `src/components/CheckoutModal.jsx` (Payment flow)
    *   `src/components/Dashboard.jsx` (Organizer view)
    *   **[NEW]** `src/components/CreateEventModal.jsx` (Includes AI Mode Selection & Generation)

### Backend (`Infinite_BZ/backend`)
*   **Framework**: FastAPI (Python)
*   **Database ORM**: SQLModel / SQLAlchemy (Async)
*   **AI Integration**: LangChain + Groq
*   **Key Modules**:
    *   `services/ticket_service.py` (PDF tickets)
    *   `services/scraper.py` (Playwright-based scraper)
    *   **[NEW]** `services/ai_generator.py` (AI Service using Llama3 on Groq)
    *   **[NEW]** `app/api/ai_routes.py` (Endpoint: `POST /api/v1/ai/generate-event`)

### Database
*   **System**: PostgreSQL 15
*   **Schema**:
    *   `events`: Stores scraped and hosted events.
    *   `user_registrations`: Tracks ticket sales.
    *   `ticket_classes`: Definitions of ticket types (VIP, General).

## 4. Key Workflows

### A. User Registration Flow
1.  User clicks "Get Ticket" on Frontend.
2.  `CheckoutModal` collects details and "mock" payment.
3.  Frontend calls `POST /registrations`.
4.  Backend:
    *   Saves registration to DB.
    *   Generates PDF Ticket with QR Code.
    *   Sends Email with PDF attachment to user.

### B. [NEW] AI Event Creation Flow
1.  User clicks "Create Event" -> Selects "AI Magic Build".
2.  Inputs a Title (e.g., "Space Tech Summit").
3.  Frontend calls `POST /api/v1/ai/generate-event`.
4.  Backend (AI Service):
    *   Calls Groq API to generate Description, Agenda, Tags.
    *   Fetches/constructs a cover image URL (via Unsplash).
5.  Frontend pre-fills the form with generated content for review.

## 5. Important Files for Context
If you need to dive deeper, read these files in the repo:

*   **`Infinite_BZ/project_structure_docs.md`**: Detailed breakdown of every file and folder.
*   **`Infinite_BZ/product_roadmap.md`**: Strategic vision and what needs to be built next.
*   **`Infinite_BZ/backend/requirements.txt`**: Added `langchain-groq` dependency.

## 6. Troubleshooting
*   **"AI Generation Failed"**: Check if `GROQ_API_KEY` is set in `Infinite_BZ/backend/.env`.
*   **Emails not sending?** Check `MAIL_USERNAME` and `MAIL_PASSWORD`.
*   **ModuleNotFoundError: 'langchain_groq'**: Run `pip install -r requirements.txt`.
