# 🧠 PlanPal – Your Conversational Calendar Assistant

PlanPal is an intelligent AI-powered assistant that helps you **book, reschedule, and cancel meetings** on your Google Calendar using natural language. Built using LangChain, FastAPI, Streamlit, and Google Calendar APIs, it offers a seamless conversational interface to manage your schedule.

> “Book a meeting with team tomorrow at 6pm”  
> “Cancel my meeting with client on Friday”  
> “Reschedule ‘DSA Review’ to Monday 10am”  

---

## 🚀 Live Demo

🔗 Frontend: 
🔗 Backend: 

> ⚠️ First response might take 20–30 seconds if backend is waking up (Render free tier spins down inactive services).

---

## 💡 Features

- 📅 Book meetings on Google Calendar
- 🔁 Reschedule existing events
- ❌ Cancel/delete events
- 🧠 Understands natural language (e.g., “next Friday”, “tomorrow 6pm”)
- 🔍 Checks availability to avoid conflicts
- 💬 Streamlit-based chat UI with memory

---

## 🧱 Tech Stack

| Layer       | Tech                              |
|-------------|-----------------------------------|
| Backend     | [FastAPI](https://fastapi.tiangolo.com)          |
| Agent       | [LangChain](https://www.langchain.com/) + OpenAI |
| Frontend    | [Streamlit](https://streamlit.io) |
| Calendar    | Google Calendar API (Service Account) |
| Deployment  | Streamlit Cloud + Render          |

---

## 🛠️ Local Setup Instructions

1. **Clone the repo**

```bash
git clone https://github.com/prakharstech/PlanPal
cd PlanPal
```

2. **Set up virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Add your credentials**

Place your creds.json in backend/
Or store Google credentials securely using .env or Render secrets

5. **Run the backend**
cd backend
uvicorn main:app --reload

6. **Run the frontend**
cd ../frontend
streamlit run app.py

## 📁 Project Structure
```bash
PlanPal/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── agent.py             # LangChain agent & tools
│   ├── calendar_utils.py    # Google Calendar integration
│   ├── creds.json           # Service account (not committed)
├── frontend/
│   ├── app.py               # Streamlit UI
│── README.md
└── requirements.txt
```

