from fastapi import FastAPI, Request
from pydantic import BaseModel
from backend.agent import run_agent  # import your LangChain agent runner
import uvicorn

app = FastAPI()

class Query(BaseModel):
    message: str

@app.post("/agent")
async def calendar_agent(query: Query):
    try:
        response = run_agent(query.message)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
