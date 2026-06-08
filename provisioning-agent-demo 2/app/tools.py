"""Agent tools: hybrid retrieval and governed actions.

Retrieval:
  search_docs   — document/policy/runbook search (for how-to, standards, step guidance)
  query_state   — exact lookup against systems-of-record tables (live state, never embed these)
  check_cidr    — overlap check against the CIDR allocation registry

Actions (governed — staged for human approval, never auto-executed):
  propose_change_request_lz — stage a Change Request for a Landing Zone build
  propose_vending_machine   — stage Vending Machine execution (the core build action)
  propose_decommission      — stage a decommission change request
"""
import json
import uuid
import pathlib
import datetime
import ipaddress

from strands import tool

_DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
DOCS  = json.loads((_DATA / "docs.json").read_text())
STATE = json.loads((_DATA / "state.json").read_text())

PENDING: dict = {}
AUDIT:   list = []


@tool
def search_docs(query: str) -> list:
    """Search internal runbooks, policy, and process documentation.

    Use for: how-to questions, step guidance, policy requirements, and standards.
    Do NOT use for live environment state — use query_state for that.
    Returns matches with source and id for citation.
    """
    terms = [t for t in query.lower().replace("/", " ").split() if len(t) > 2]
    hits  = []
    for d in DOCS:
        hay   = (d["title"] + " " + d["text"]).lower()
        score = sum(1 for t in terms if t in hay)
        if score:
            hits.append((score, d))
    hits.sort(key=lambda x: -x[0])
    return [{"source": d["source"], "id": d["id"], "title": d["title"], "snippet": d["text"][:300]}
            for _, d in hits[:5]]


@tool
def query_state(entity: str, key: str = "") -> list:
    """Query systems-of-record tables for live, exact state. Always prefer this over documents for current values.

    entity: one of step_definitions, landing_zones, step_tracker, cidr_allocations, tickets, pipelines.
    key:    optional filter matched against any field value (e.g. an lz_id, team name, or status).
    """
    rows = STATE.get(entity, [])
    if key:
        k    = key.lower()
        rows = [r for r in rows if k in json.dumps(r).lower()]
    return rows


@tool
def check_cidr(cidr: str) -> dict:
    """Check whether a candidate CIDR overlaps any allocated block. Read-only; safe to call freely."""
    try:
        net = ipaddress.ip_network(cidr, strict=False)
    except ValueError as e:
        return {"error": str(e)}
    conflicts = [c for c in STATE.get("cidr_allocations", []) if net.overlaps(ipaddress.ip_network(c))]
    return {"cidr": cidr, "available": not conflicts, "conflicts_with": conflicts}


def _propose(action_type: str, summary: str, params: dict) -> dict:
    action_id         = "ACT-" + uuid.uuid4().hex[:6].upper()
    PENDING[action_id] = {
        "id":          action_id,
        "type":        action_type,
        "summary":     summary,
        "params":      params,
        "proposed_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    return {"status": "proposed", "action_id": action_id, "summary": summary,
            "note": "Staged for human approval. Not executed."}


@tool
def propose_change_request_lz(lz_id: str, summary: str) -> dict:
    """Propose a Change Request for a Landing Zone build action.
    The active CRQ is required before the Vending Machine can execute.
    Stages the action for approval — does NOT submit it.
    """
    return _propose("create_change_request",
                    f"Change Request for {lz_id}: {summary}",
                    {"lz_id": lz_id, "summary": summary})


@tool
def propose_vending_machine(lz_id: str, action_summary: str) -> dict:
    """Propose execution of the Account Vending Machine for a Landing Zone.
    This is the core build action that provisions the environment.
    An approved Change Request must already be staged or active.
    Stages the action for approval — does NOT execute it.
    """
    return _propose("run_vending_machine",
                    f"Run Vending Machine for {lz_id}: {action_summary}",
                    {"lz_id": lz_id, "action_summary": action_summary})


@tool
def propose_decommission(lz_id: str, reason: str) -> dict:
    """Propose decommissioning a Landing Zone (raises a change request on approval).
    Eligibility must be confirmed before calling this.
    Stages the action for approval — does NOT execute it.
    """
    return _propose("decommission",
                    f"Decommission {lz_id}: {reason}",
                    {"lz_id": lz_id, "reason": reason})


def execute(action_id: str):
    """Approve and execute a staged action; record it to the audit log. Called by the server only."""
    action = PENDING.pop(action_id, None)
    if not action:
        return None
    action["approved_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    AUDIT.append(action)
    return action


def discard(action_id: str):
    """Reject a staged action. Called by the server only."""
    return PENDING.pop(action_id, None)
