# Intelligent LLM-Based Automated Code Review and Auto-Fix System

A modern full-stack web application that allows developers to write or paste code in multiple languages (Python, JavaScript, Java, C++), performs instant static analysis using LLMs, lists detected issues grouped by severity and category, displays visual side-by-side differences of corrections, and allows one-click auto-fixes.

---

## Features

- **Premium UI/UX**: Sleek dark mode design with modern glassmorphism panels, interactive circular score indicators, and smooth animations.
- **Monaco Code Editor**: Professional syntax highlighting, line numbers, and developer editing tools using Microsoft Monaco Editor.
- **Interactive Issue Tracking**: Clear breakdown of bugs, security vulnerabilities, performance bottlenecks, and style violations with line numbers and fix suggestions.
- **Side-by-Side Diff Viewer**: Real-time code comparisons highlighting insertions and deletions in a synchronized view.
- **One-Click Apply Auto-Fix**: Directly updates the editor with corrected code in a single click.
- **Persistent History**: Keeps records of all past reviews saved in a PostgreSQL/SQLite database.
- **Fail-Safe Fallbacks**:
  - **Database**: Automatically falls back to a local SQLite database (`code_review.db`) if no PostgreSQL connection URL is provided.
  - **LLM API**: Automatically falls back to a friendly "Demo Mode" with simulated review suggestions if no live API keys are provided.

---

## Tech Stack

- **Frontend**: React.js (Vite, Monaco Editor, Lucide Icons, Glassmorphic CSS)
- **Backend**: FastAPI (Python 3.11+, SQLAlchemy, Uvicorn, Dotenv)
- **Database**: PostgreSQL (Production) / SQLite (Development fallback)
- **AI Integrations**: Gemini API (via direct HTTP, defaults to `gemini-2.5-flash`) or OpenAI API (`gpt-4-turbo-preview`)

---

## Quick Start Setup

### 1. Set Up Environment Variables

Create a `.env` file in the project root directory:

```ini
# Server settings
PORT=8000
HOST=127.0.0.1

# Database Configuration (Defaults to SQLite if left as-is)
DATABASE_URL=sqlite:///./code_review.db

# LLM Configuration (Add your key here to enable live AI analysis)
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Start the Backend (FastAPI)

1. Open a terminal in the project root directory.
2. Initialize and activate the virtual environment:
   ```powershell
   # Windows PowerShell
   python -m venv backend/venv
   backend/venv/Scripts/Activate.ps1
   ```
3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Launch the server:
   ```bash
   python -m backend.app.main
   ```
   The backend service will start running on [http://localhost:8000](http://localhost:8000).

### 3. Start the Frontend (React + Vite)

1. Open a new terminal in the project root directory.
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Install packages:
   ```bash
   npm install
   ```
4. Run the development server:
   ```bash
   npm run dev
   ```
   Open your browser to the URL output in the terminal (usually [http://localhost:5173](http://localhost:5173)).
