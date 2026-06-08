"""Cross-session memory store.

Persists key facts to a JSON file between sessions.
Swap _STORE for a DynamoDB table in production — only load() and save() change.

Every agent call receives a context_prefix() built from stored facts.
extract_and_save() runs after each turn to capture what was discussed.
"""
import json
import re
import pathlib
import datetime

_STORE = pathlib.Path(__file__).resolve().parent.parent / "data" / "memory.json"
_MAX   = 12


def load() -> list:
    try:
        return json.loads(_STORE.read_text())
    except Exception:
        return []


def save(facts: list):
    _STORE.write_text(json.dumps(facts[-_MAX:], indent=2))


def add_facts(new_facts: list):
    existing       = load()
    existing_texts = {f["fact"] for f in existing}
    for f in new_facts:
        if f not in existing_texts:
            existing.append({
                "fact": f,
                "ts":   datetime.datetime.now().isoformat(timespec="seconds"),
            })
    save(existing)


def clear():
    save([])


def context_prefix() -> str:
    """Build a context string injected at the top of every agent call."""
    facts = load()
    if not facts:
        return ""
    lines = "\n".join(f"- {f['fact']}" for f in facts[-6:])
    return (
        "Remembered context from previous sessions "
        "(use this to provide continuity without being told again):\n"
        f"{lines}\n\n"
    )


def extract_and_save(user_msg: str, reply: str, trace: list):
    """Extract memorable facts from the current turn and persist them."""
    combined = " ".join([user_msg, reply] + [s.get("output", "") for s in trace])
    new_facts = []

    # Landing Zone IDs
    lz_ids = list(dict.fromkeys(re.findall(r"LZ-\d+", combined)))
    for lz_id in lz_ids[:3]:
        new_facts.append(f"{lz_id} was discussed")

    # Teams
    teams = list(dict.fromkeys(re.findall(r"Team\s+\w+", combined)))
    for team in teams[:2]:
        new_facts.append(f"{team} was involved in a request")

    # Pipeline execution summary
    if trace:
        names = [s["agent"] for s in trace]
        label = " → ".join(names[:3]) + ("..." if len(names) > 3 else "")
        new_facts.append(f"Pipeline ran: {label}")

    # Action context
    outputs = " ".join(s.get("output", "") for s in trace).lower()
    if "change request" in outputs and lz_ids:
        new_facts.append(f"A Change Request was proposed for {lz_ids[0]}")
    if "vending machine" in outputs and lz_ids:
        new_facts.append(f"Vending Machine execution was proposed for {lz_ids[0]}")
    if "decommission" in combined.lower() and lz_ids:
        new_facts.append(f"Decommission was discussed for {lz_ids[0]}")

    if new_facts:
        add_facts(new_facts)
