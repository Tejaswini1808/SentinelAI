import logging

from fastapi import FastAPI

from app.routers import agents, alerts, chat, incidents, investigate, metrics, search

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="SentinelAI",
    description="Multi-Agent Autonomous Security Operations Platform",
    version="0.1.0",
)

app.include_router(alerts.router)
app.include_router(investigate.router)
app.include_router(incidents.router)
app.include_router(chat.router)
app.include_router(search.router)
app.include_router(metrics.router)
app.include_router(agents.router)


@app.get("/")
def root():
    return {"service": "SentinelAI", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}
