"""Request-scoped progress events for live UI visibility.

The streaming chat endpoint runs the agent on a worker thread and sets a per-request
sink (a queue). As agents, pipeline steps, and action proposals execute, they call
emit() — those events are drained by the endpoint and forwarded to the browser as
Server-Sent Events, so the user sees the bot routing, consulting sources, running
steps, and (crucially) staging actions *as it happens*.

When no sink is set (the plain /api/chat endpoint), emit() is a no-op, so the same
instrumentation is harmless on the non-streaming path.
"""
import threading

_local = threading.local()


def set_sink(q):
    _local.q = q


def clear_sink():
    _local.q = None


def emit(event: dict):
    q = getattr(_local, "q", None)
    if q is not None:
        q.put(event)
