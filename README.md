# 🧠 PlanPal – A Conversational Calendar Assistant

PlanPal is an intelligent AI-powered assistant that helps you **book, reschedule, and cancel meetings** on your Google Calendar using natural language. Built using LangChain, FastAPI, **React (Vite)**, and Google Calendar APIs, it offers a seamless conversational interface to manage your schedule.

> “Book a meeting with team tomorrow at 6pm”  
> “Cancel my meeting with client on Friday”  
> “Reschedule ‘DSA Review’ to Monday 10am”  

---

## 🚀 Live Demo

🔗 https://plan-pal-ten.vercel.app

> ⚠️ First response might take a minute if backend is waking up (Render free tier spins down inactive services).

---

## 💡 Features

- 📅 **Book meetings:** Parses natural language to schedule new events.
- 🔁 **Reschedule events:** Finds and updates existing events.
- ❌ **Cancel/delete events:** Removes events from your calendar.
- 🧠 **Understands context:** Knows "next Friday" or "tomorrow 6pm".
- 🔍 **Checks availability:** Checks for conflicts before booking.
- 💬 **React-based chat UI:** A clean, modern chat interface with Google Auth integration.

---

## 🧱 Tech Stack

| Layer       | Tech                              |
|-------------|-----------------------------------|
| Backend     | [FastAPI](https://fastapi.tiangolo.com)          |
| Agent       | [LangChain](https://www.langchain.com/) + MistralAI |
| Frontend    | [React (Vite)](https://vitejs.dev) |
| Calendar    | Google Calendar API (OAuth 2.0) |
| Deployment  | Vercel (Frontend) + Render (Backend)          |

---

## 🛠️ Local Setup Instructions

### 1. Backend (Python/FastAPI)

1.  **Navigate to backend:**
    ```bash
    cd backend
    ```
2.  **Set up virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # (or .\.venv\Scripts\activate on Windows)
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r ../requirements.txt
    ```
    (Note: `requirements.txt` is in the root directory)
4.  **Add your credentials:**
    * Place your `client_secret.json` file in the `backend/` directory from your Google Cloud Console credentials.
    * Create a `.env` file in the `backend/` directory with your `MISTRAL_API_KEY`.
5.  **Run the backend:**
    ```bash
    fastapi dev main.py
    ```
    The backend will be running at `http://127.0.0.1:8000`.

### 2. Frontend (React/Vite)

1.  **Navigate to frontend (in a new terminal):**
    ```bash
    cd frontend/PlanPalFE
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Add environment variables:**
    * Create a `.env` file in the `frontend/PlanPalFE/` directory.
    * Add your Google Client ID (must match the one used in `client_secret.json`):
        `VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com`
4.  **Run the frontend:**
    ```bash
    npm run dev
    ```
    The React app will be running at `http://localhost:5173`.

---

## 📁 Project Structure
```bash
PlanPal/
├── backend/
│   ├── main.py              # FastAPI app (handles auth, agent)
│   ├── agent.py             # LangChain agent & tools
│   ├── calendar_utils.py    # Google Calendar integration
│   ├── client_secret.json   # Google OAuth credentials (not committed)
│   └── .env                 # Mistral API Key (not committed)
├── frontend/
│   ├── PlanPalFE/           # React + Vite frontend
│   │   ├── src/
│   │   │   ├── App.jsx      # Main chat component
│   │   │   ├── Login.jsx    # Google OAuth login component
│   │   │   ├── main.jsx     # App entrypoint
│   │   │   └── Calendar.jsx # Google Calendar embed
│   │   ├── package.json     # Node dependencies
│   │   └── .env             # Google Client ID (not committed)
│   └── app.py               # (Old Streamlit app)
│── README.md                # This file
└── requirements.txt         # Python dependencies
