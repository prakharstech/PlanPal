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
from google.auth.transport import requests

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

CLIENT_SECRET_FILE = 'backend/client_secret.json'


# --- API Endpoints ---
@app.get("/")
def health_check():
    return {"status": "ok", "message": "PlanPal backend is running!"}

@app.post("/auth/google")
async def auth_google(auth_code: AuthCode):
    """Exchanges an authorization code for user credentials and info."""
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            scopes=SCOPES,
            redirect_uri='https://plan-pal-ten.vercel.app'
        )
        flow.fetch_token(code=auth_code.code)
        credentials = flow.credentials
        
        # Decode the ID token to get user info
        request = requests.Request()
        id_info = id_token.verify_oauth2_token(
            credentials.id_token, request, flow.client_config['client_id']
        )
        
        # Return both the access token and the user's email
        return {
            "token": credentials.token,
            "user": {
                "email": id_info.get("email"),
                "name": id_info.get("name")
            }
        }
        
    except Exception as e:
        print(f"!!! IMPORTANT OAUTH ERROR !!! ---> {e}")
        raise HTTPException(status_code=400, detail=f"Failed to exchange auth code: {str(e)}")

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