# InfiniteBZ - Chennai's Premier Business Event Platform

**InfiniteBZ** is a specialized event discovery and management platform dedicated strictly to the **Business, Tech, and Startup community in Chennai**. It filters out noise (entertainment, music, sports) to provide a professional ecosystem for networking and growth.

## 🌟 Key Features

- **Exclusive Business Focus**: Aggregates high-quality events from Trade Centre (CTC), AllEvents, Meetup, and Eventbrite, filtering out non-business categories automatically.
- **AI-Powered Event Generation**: Magic Build mode powered by Groq (LLM) auto-generates event contents, while Pollinations.ai generates contextual hero cover images. 
- **Full Backend Automation**: Built-in Playwright scraping to continually scan for and pull the newest events online.
- **Unified Ticketing Registration**: First-class handling of VIP/Early Bird/Free tickets, generating dynamic QR-coded PDF tickets, sending email confirmations, and settling paid transactions via Razorpay.

---

## 🛠️ Tech Stack

### 🔹 Backend
- **Language**: Python 3.10+
- **Framework**: FastAPI (Asynchronous API endpoints)
- **Database**: PostgreSQL (via Async/Await SQLAlchemy)
- **Scraping**: Playwright headless browser combined with Beautiful Soup
- **AI Automation**: LangChain + Groq API integration 

### 🔹 Frontend
- **Framework**: React.js bundled via Vite
- **Styling**: Tailwind CSS (Modern Glassmorphism aesthetics)
- **Icons**: Lucide React

---

## 🚀 Getting Started & Setup

Follow these steps closely to set up both the backend and frontend servers on your local machine.

### Prerequisites

Ensure you have installed:
1. [Python 3.10 or higher](https://www.python.org/downloads/)
2. [Node.js 18 or higher](https://nodejs.org/en)
3. [PostgreSQL Server](https://www.postgresql.org/download/) (Installed and running on your machine)

### Phase 1: Database Setup

1. Open your PostgreSQL terminal (psql) or pgAdmin.
2. Create a new empty database named `infinite_bz`:
   ```sql
   CREATE DATABASE infinite_bz;
   ```

### Phase 2: Backend Setup

The backend handles the APIs, database connection, and all the Python scraping automated systems.

1. Navigate to the `backend` folder via terminal:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv env
   
   # For Windows
   .\env\Scripts\activate
   
   # For Mac/Linux
   source env/bin/activate
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Install the headless Playwright browser binaries required for scraping events:
   ```bash
   playwright install
   ```
5. Create a file named `.env` in the `backend/` folder. Add the following required configurations and insert your own secure credentials. (If you don't have API keys yet, you can leave Groq and Email settings blank for initial testing, but the database URL is required):

   ```env
   # Database Configuration
   DATABASE_URL=postgresql+asyncpg://postgres:yourdatabasepassword@localhost:5432/infinite_bz
   
   # Security Keys
   SECRET_KEY=generate_a_random_secure_hex_code
   ALGORITHM=HS256
   
   # AI API Keys 
   GROQ_API_KEY=your_groq_api_key
   
   # Mailing System Credentials (For sending tickets)
   MAIL_USERNAME=your_gmail_address@gmail.com
   MAIL_PASSWORD=your_gmail_app_password
   MAIL_FROM=your_gmail_address@gmail.com
   MAIL_PORT=587
   MAIL_SERVER=smtp.gmail.com
   ```
6. Run the local backend server application:
   ```bash
   python run.py
   ```
   *The backend should now successfully be running on `http://localhost:8000`. It will auto-initialize necessary database tables on its first startup.*

### Phase 3: Frontend Setup

The frontend provides the main dashboard and visual user experience. 

1. Open a **new separate terminal** window and navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install the necessary Node packages (NPM will read the `package.json` configurations):
   ```bash
   npm install
   ```
3. Boot up the Vite React server locally:
   ```bash
   npm run dev
   ```

You are done! Open up your browser and navigate to `http://localhost:5173` to see your running InfiniteBZ platform. 

---

## 👩‍💻 Operating Guide

- **Checking your Scraping System**: To manually test or schedule the background automated scraping module, you can directly execute the python module from within your activated backend terminal: 
  ```bash
  python robust_scrape.py
  ```
- **Login / Accounts**: To access the developer or host dashboard features on the frontend, simply create a new user account on the login page of your local `http://localhost:5173`.
