# ping_service.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/ping")
def ping():
    return {"response": "pong"}
