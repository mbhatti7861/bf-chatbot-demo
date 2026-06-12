"""Governed write actions.

Consequential changes (raising a ServiceNow Change Request, running the Vending
Machine, decommissioning a Landing Zone) are never auto-executed. Each is staged
as a pending proposal; a human approves in the UI; only then is it recorded to an
immutable audit log. In production these proposals become Lambda-backed actions
keyed to an RBAC role, with the audit log in DynamoDB.
"""
import uuid
import datetime

from strands import tool

from . import events

PENDING: dict = {}
AUDIT:   list = []


def _propose(action_type: str, summary: str, params: dict) -> dict:
    # Surface the intent BEFORE staging, so the user sees the bot is about to
    # request a consequential action (it still requires human approval).
    events.emit({"type": "action", "text": f"Staging for approval — {summary}"})
    action_id = "ACT-" + uuid.uuid4().hex[:6].upper()
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
    """Propose a ServiceNow Change Request for a Landing Zone build action.
    An approved CRQ is required before the Vending Machine can execute.
    Stages the action for approval — does NOT submit it.
    """
    return _propose("create_change_request",
                    f"ServiceNow CRQ for {lz_id}: {summary}",
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
    """Propose decommissioning a Landing Zone (raises a ServiceNow CRQ on approval).
    Eligibility must be confirmed before calling this.
    Stages the action for approval — does NOT execute it.
    """
    return _propose("decommission",
                    f"Decommission {lz_id}: {reason}",
                    {"lz_id": lz_id, "reason": reason})


def execute(action_id: str):
    """Approve and execute a staged action; record it to the audit log. Server only."""
    action = PENDING.pop(action_id, None)
    if not action:
        return None
    action["approved_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    AUDIT.append(action)
    return action


def discard(action_id: str):
    """Reject a staged action. Server only."""
    return PENDING.pop(action_id, None)
