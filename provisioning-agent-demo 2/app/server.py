"""FastAPI server. Run with: uvicorn app.server:app --reload"""
import json
import queue
import pathlib
import threading

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from .agents import build_supervisor
from . import actions, sources, pipeline, memory, events

app   = FastAPI(title="Forge — LZ Provisioning Agent (demo)")
agent = build_supervisor()
WEB   = pathlib.Path(__file__).resolve().parent.parent / "web"


@app.on_event("startup")
def _warm_indexes():
    """Embed the KB/Confluence corpora once at boot (or fall back to keyword)."""
    try:
        sources.warmup()
    except Exception:
        pass


class ChatIn(BaseModel):
    message: str


@app.post("/api/chat")
def chat(body: ChatIn):
    pipeline.TRACE.clear()
    before = set(actions.PENDING)
    reply  = str(agent(memory.context_prefix() + body.message))
    new_actions = [actions.PENDING[a] for a in actions.PENDING if a not in before]
    memory.extract_and_save(body.message, reply, list(pipeline.TRACE))
    return {
        "reply":           reply,
        "pending_actions": new_actions,
        "trace":           list(pipeline.TRACE),
        "memory":          memory.load(),
    }


def _sse(obj: dict) -> str:
    return f"data: {json.dumps(obj)}\n\n"


@app.post("/api/chat/stream")
def chat_stream(body: ChatIn):
    """Same as /api/chat, but streams live progress events while the agent works:
    routing, each specialist consulted, each pipeline step, and every action staged
    for approval — followed by a final 'done' event with the full result.
    """
    q: queue.Queue = queue.Queue()
    result: dict = {}

    def worker():
        events.set_sink(q)
        pipeline.TRACE.clear()
        before = set(actions.PENDING)
        try:
            reply = str(agent(memory.context_prefix() + body.message))
            new_actions = [actions.PENDING[a] for a in actions.PENDING if a not in before]
            memory.extract_and_save(body.message, reply, list(pipeline.TRACE))
            result.update(reply=reply, pending_actions=new_actions,
                          trace=list(pipeline.TRACE), memory=memory.load())
        except Exception as e:  # surface failures to the client instead of hanging
            result["error"] = str(e)
        finally:
            events.clear_sink()
            q.put(None)  # sentinel: worker finished

    threading.Thread(target=worker, daemon=True).start()

    def stream():
        yield _sse({"type": "status", "text": "Routing your request…"})
        while True:
            ev = q.get()
            if ev is None:
                break
            yield _sse(ev)
        if result.get("error"):
            yield _sse({"type": "error", "text": result["error"]})
        else:
            yield _sse({"type": "done",
                        "reply": result.get("reply", ""),
                        "pending_actions": result.get("pending_actions", []),
                        "trace": result.get("trace", []),
                        "memory": result.get("memory", {})})

    return StreamingResponse(stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})


@app.get("/api/sources")
def get_sources():
    """The data-source connector registry — drives the UI Data Sources panel."""
    mode    = sources.retrieval_backend()
    backend = "Titan v2 + FAISS" if mode == "vector" else "keyword (fallback)"
    rows    = []
    for s in sources.SOURCES:
        s = dict(s)
        if s["kind"] == "document":
            s["backend"] = backend
        rows.append(s)
    return {"sources": rows, "retrieval": mode}


@app.post("/api/session/new")
def new_session():
    """Start a fresh conversation. Memory persists — the new agent session inherits it."""
    global agent
    agent = build_supervisor()
    return {"ok": True, "memory": memory.load()}


@app.get("/api/memory")
def get_memory():
    return {"memory": memory.load()}


@app.delete("/api/memory")
def clear_memory():
    memory.clear()
    return {"ok": True, "memory": memory.load()}


@app.post("/api/actions/{action_id}/approve")
def approve(action_id: str):
    executed = actions.execute(action_id)
    if executed:
        # Approval is a durable decision — record it to memory so future sessions
        # know it happened. (The thing approved is durable; its live effect is not.)
        memory.record_decision(f"Approved {executed['type']}: {executed['summary']}", key=executed["id"])
    return {"ok": executed is not None, "executed": executed,
            "audit_count": len(actions.AUDIT), "memory": memory.load()}


@app.post("/api/actions/{action_id}/reject")
def reject(action_id: str):
    rejected = actions.discard(action_id)
    if rejected:
        memory.record_decision(f"Rejected {rejected['type']}: {rejected['summary']}", key="rej-" + rejected["id"])
    return {"ok": rejected is not None, "memory": memory.load()}


@app.get("/api/audit")
def audit():
    return {"audit": actions.AUDIT}


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")
