# metrics_service.py
from fastapi import FastAPI
import psutil

app = FastAPI()

# Root endpoint (for health check / default path)
@app.get("/")
def root():
    return {"status": "ok", "service": "metrics-service"}

# Metrics endpoint
@app.get("/metrics")
def get_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    return {
        "cpu_percent": cpu_usage,
        "memory_percent": memory.percent,
        "total_memory_gb": round(memory.total / (1024 ** 3), 2),
        "used_memory_gb": round(memory.used / (1024 ** 3), 2),
    }
