"""Consistent cross-session memory.

Design principle — consistency by construction:

  Durable facts are remembered. Volatile state is not.
    We store the *identity* of things the user has worked with (which Landing
    Zones, teams, tickets, features) and *decisions taken* (approved/rejected
    actions). We deliberately do NOT store mutable values like current build
    step or ticket status — those are always re-queried live from ServiceNow /
    Jira at answer time. This is what keeps memory from ever contradicting the
    systems of record: memory holds what *was decided*, the sources hold what
    *is true now*.

  Entity-keyed, idempotent upserts.
    Facts are keyed by entity id, not appended as free text. Re-seeing an entity
    refreshes its `last_seen` and re-enriches its label from the authoritative
    source — it never creates a second, divergent copy. Decisions are deduped by
    action id. So the store stays internally consistent no matter how many turns
    reference the same thing.

Swap _STORE for a DynamoDB table in production — only load() and save() change.
"""
import re
import json
import pathlib
import datetime

from . import sources

_STORE = pathlib.Path(__file__).resolve().parent.parent / "data" / "memory.json"
_MAX_ENTITIES  = 12
_MAX_DECISIONS = 10

# id pattern -> (entity type, enrichment source)
_PATTERNS = [
    (re.compile(r"\bLZ-\d+\b"),   "landing_zone"),
    (re.compile(r"\bTeam\s+[\w-]+"), "team"),
    (re.compile(r"\bRITM-\d+\b"), "servicenow_request"),
    (re.compile(r"\bINC-\d+\b"),  "servicenow_incident"),
    (re.compile(r"\bCRQ-\d+\b"),  "servicenow_change"),
    (re.compile(r"\bFEAT-\d+\b"), "jira_feature"),
    (re.compile(r"\bLZB-\d+\b"),  "jira_story"),
]


def _blank() -> dict:
    return {"entities": {}, "decisions": []}


def load() -> dict:
    try:
        data = json.loads(_STORE.read_text(encoding="utf-8"))
        data.setdefault("entities", {})
        data.setdefault("decisions", [])
        return data
    except Exception:
        return _blank()


def save(data: dict):
    # Bound the store; keep the most recently seen entities and latest decisions.
    ents = dict(sorted(data["entities"].items(),
                       key=lambda kv: kv[1].get("last_seen", ""), reverse=True)[:_MAX_ENTITIES])
    data = {"entities": ents, "decisions": data["decisions"][-_MAX_DECISIONS:]}
    _STORE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def clear():
    _STORE.write_text(json.dumps(_blank(), indent=2, ensure_ascii=False), encoding="utf-8")


def _now() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def _label_for(entity_id: str, etype: str) -> str:
    """Build a STABLE label by enriching from the authoritative source.

    Only identity attributes are pulled (team / region / type / short description) —
    never volatile status — so the remembered label cannot drift out of sync.
    """
    if etype == "landing_zone":
        for ci in sources.SERVICENOW["cmdb_ci_landing_zone"]:
            if ci["lz_id"] == entity_id:
                return f"{ci['team']} · {ci['region']} · {ci['type']}"
    if etype == "team":
        team = entity_id.strip()
        for ci in sources.SERVICENOW["cmdb_ci_landing_zone"]:
            if ci["team"].lower() == team.lower():
                return f"owns {ci['lz_id']} ({ci['region']})"
    if etype.startswith("servicenow_"):
        table = {"servicenow_request": "request",
                 "servicenow_incident": "incident",
                 "servicenow_change": "change_request"}[etype]
        for r in sources.SERVICENOW.get(table, []):
            if r.get("number") == entity_id:
                return r.get("short_description", "")
    if etype == "jira_feature":
        for f in sources.JIRA["feature"]:
            if f["key"] == entity_id:
                return f["summary"]
    if etype == "jira_story":
        for s in sources.JIRA["story"]:
            if s["key"] == entity_id:
                return s["summary"]
    return ""


def note_entities(text: str):
    """Upsert every entity mentioned in `text`. Idempotent and keyed by id."""
    data = load()
    seen = set()
    for pattern, etype in _PATTERNS:
        for raw in pattern.findall(text):
            eid = re.sub(r"\s+", " ", raw).strip()
            if eid in seen:
                continue
            seen.add(eid)
            ent = data["entities"].get(eid, {"id": eid, "type": etype, "first_seen": _now()})
            ent["type"]      = etype
            ent["label"]     = _label_for(eid, etype) or ent.get("label", "")
            ent["last_seen"] = _now()
            data["entities"][eid] = ent
    save(data)


def record_decision(text: str, key: str = ""):
    """Append a durable decision (e.g. an approval). Deduped by key when given."""
    data = load()
    if key and any(d.get("key") == key for d in data["decisions"]):
        return
    data["decisions"].append({"text": text, "key": key, "ts": _now()})
    save(data)


def context_prefix() -> str:
    """Context injected at the top of every supervisor call."""
    data = load()
    ents = sorted(data["entities"].values(), key=lambda e: e.get("last_seen", ""), reverse=True)
    if not ents and not data["decisions"]:
        return ""
    lines = ["Remembered context from earlier work (continuity across sessions).",
             "Durable only — re-query ServiceNow/Jira for any current status:"]
    for e in ents[:6]:
        label = f" — {e['label']}" if e.get("label") else ""
        lines.append(f"- {e['id']} ({e['type']}){label}")
    for d in data["decisions"][-4:]:
        lines.append(f"- decision: {d['text']}")
    return "\n".join(lines) + "\n\n"


def extract_and_save(user_msg: str, reply: str, trace: list):
    """Capture durable entities from the turn. Volatile status is intentionally ignored."""
    combined = " ".join([user_msg, reply] + [s.get("output", "") for s in trace])
    note_entities(combined)
