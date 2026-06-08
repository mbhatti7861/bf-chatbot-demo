"""FastAPI server. Run with: uvicorn app.server:app --reload"""
import pathlib

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .agents import build_supervisor
from . import tools, pipeline

app = FastAPI(title="Cloud Provisioning Agent (demo)")
agent = build_supervisor()
WEB = pathlib.Path(__file__).resolve().parent.parent / "web"


class ChatIn(BaseModel):
    message: str


@app.post("/api/chat")
def chat(body: ChatIn):
    pipeline.TRACE.clear()
    before = set(tools.PENDING)
    reply = str(agent(body.message))
    new_actions = [tools.PENDING[a] for a in tools.PENDING if a not in before]
    return {"reply": reply, "pending_actions": new_actions, "trace": list(pipeline.TRACE)}


@app.post("/api/actions/{action_id}/approve")
def approve(action_id: str):
    executed = tools.execute(action_id)
    return {"ok": executed is not None, "executed": executed, "audit_count": len(tools.AUDIT)}


@app.post("/api/actions/{action_id}/reject")
def reject(action_id: str):
    return {"ok": tools.discard(action_id) is not None}


@app.get("/api/audit")
def audit():
    return {"audit": tools.AUDIT}


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")
