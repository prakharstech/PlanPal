# backend/main.py
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel # Ensure BaseModel is imported
from fastapi.middleware.cors import CORSMiddleware
from backend.agent import run_agent
import uvicorn
from typing import Optional
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.oauth2 import id_token
import requests
from google.auth.transport.requests import Request
import os


app = FastAPI()

# --- Pydantic Models ---
class Query(BaseModel):
    message: str

class AuthCode(BaseModel):
    code: str

# --- CORS Configuration ---
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "https://plan-pal-ten.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Google Auth Configuration ---
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

CLIENT_SECRET_FILE = 'client_secret.json'


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "postmessage"

# --- API Endpoints ---
@app.get("/")
def health_check():
    return {"status": "ok", "message": "PlanPal backend is running!"}

@app.post("/auth/google")
def google_auth(auth_code: AuthCode):

    token_url = "https://oauth2.googleapis.com/token"

    data = {
        "code": auth_code.code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    r = requests.post(token_url, data=data)

    if r.status_code != 200:
        raise HTTPException(400, f"Token exchange failed: {r.text}")

    tokens = r.json()

    # Decode ID token
    id_info = id_token.verify_oauth2_token(
    tokens["id_token"],
    Request(),            
    GOOGLE_CLIENT_ID
)


    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "email": id_info["email"],
        "name": id_info["name"]
    }
        

@app.post("/agent")
async def calendar_agent(query: Query, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    
    token = authorization.split("Bearer ")[1]
    
    try:
        response = run_agent(query.message, token)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
