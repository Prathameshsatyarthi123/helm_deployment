# ping_service.py
from fastapi import FastAPI

app = FastAPI()

# Root endpoint (for health check / default path)
@app.get("/")
def root():
    return {"status": "ok", "service": "ping-service"}

# Ping endpoint
@app.get("/ping")
def ping():
    return {"response": "pong-upd"}
