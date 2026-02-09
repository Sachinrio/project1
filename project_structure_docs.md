# Infinite BZ - Project Structure Analysis

## Overview
**Infinite BZ** is a full-stack event management platform built with a modern tech stack focused on performance and scalability.
- **Frontend**: React (Vite) + Tailwind CSS
- **Backend**: Python (FastAPI) + PostgreSQL (Async)
- **Scraping**: Playwright + BeautifulSoup

## 📂 Project Directory Breakdown

### 1. Frontend (`/frontend`)
The user interface is built with React and Vite for fast development.

*   `src/components/`: Modular UI components.
    *   **Core Pages**: `Dashboard.jsx`, `LandingPage.jsx`, `SettingsPage.jsx`, `MyRegistrationsPage.jsx`.
    *   **Event Management**: `CreateEventPage.jsx`, `CreateEventModal.jsx`, `TicketManager.jsx`.
    *   **Shared UI**: `Sidebar.jsx`, `EventFeed.jsx`, `EventDetailModal.jsx`, `CheckoutModal.jsx`.
    *   **Utilities**: `MarkdownEditor.jsx`, `ImageGalleryUploader.jsx`.
    *   **Auth**: `AuthPage.jsx` (Login/Signup).
*   `src/App.jsx`: Main application router setup.
*   `vite.config.js`: Configuration for the Vite build tool and dev server.

### 2. Backend (`/backend`)
A high-performance asynchronous API using FastAPI.

*   `app/`
    *   `api/`: API Endpoints.
        *   `routes.py`: Main event routes (list, create, sync).
        *   `auth_routes.py`: Authentication (Login, Signup, Google Auth).
        *   `registrations_endpoints.py`: **[NEW]** User registration & ticket fetching.
    *   `core/`: Core configuration.
        *   `database.py`: Async Database connection setup.
        *   `security.py`: JWT token handling and password hashing.
        *   `email_utils.py`: **[UPDATED]** Email sending logic + PDF attachment.
    *   `models/`: Database Schemas (Table definitions).
        *   `schemas.py`: Defines `Event`, `User`, `UserRegistration`, `TicketClass` tables.
    *   `services/`: Business Logic.
        *   `scraper.py`: Playwright scraper for Eventbrite/Meetup.
        *   `auth_service.py`: User management logic.
        *   `ticket_service.py`: **[NEW]** PDF Ticket generation (ReportLab).
*   **Root Scripts**:
    *   `run.py`: Entry point to start the server.
    *   `migrate_schema.py`: **[NEW]** Script to handle DB migrations (add columns).
    *   `sync_patch.py`: Utility for applying DB schema updates manually.

### 3. Database (`PostgreSQL`)
*   **Tables**: `user`, `event`, `userregistration`, `ticketclass`.
*   **Status**: Schema update includes `JSONB` columns for flexible data storage.

## 🔄 Key Workflows
1.  **Event Aggregation**: `scraper.py` fetches external events -> `routes.py` (sync endpoint) saves to DB.
2.  **Registration Flow**:
    *   **User**: Selects Tickets -> Enters Details -> "Pays" (Mock).
    *   **Frontend**: `CheckoutModal.jsx` sends payload to `registrations_endpoints.py`.
    *   **Backend**: Saves `UserRegistration` -> Generates PDF (`ticket_service.py`) -> Emails User (`email_utils.py`).
3.  **Event Creation**: `id` generated as `chk-{uuid}` -> stored as Internal Event (`source='InfiniteBZ'`).
