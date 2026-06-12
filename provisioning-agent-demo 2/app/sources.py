"""The four data-source connectors.

Each enterprise system is a first-class, named connector with its own tool and
its own citation format. Two retrieval shapes are deliberately distinguished:

  unstructured / document search  →  Knowledge Base, Confluence
      Free-text questions ("how do I...", policy, standards) go through semantic
      vector search: docs are embedded with Amazon Titan Text Embeddings V2 and
      retrieved from an in-process FAISS index (see retrieval.py). Returns cited
      snippets. In production these become a Bedrock Knowledge Base Retrieve call.

  structured / systems-of-record  →  ServiceNow, Jira
      Live records (tickets, CMDB CIs, issues, sprints) are answered by exact
      lookups against tables — never embedded in a vector store, because their
      values change and stale embeddings would give wrong answers. In production
      these become real ServiceNow / Jira REST API calls.

SOURCES is the registry the UI and blueprint render from — one row per connector.
"""
import json
import pathlib
import ipaddress

from strands import tool

from . import retrieval

_DATA = pathlib.Path(__file__).resolve().parent.parent / "data"


def _load(name: str):
    return json.loads((_DATA / name).read_text(encoding="utf-8"))


KB         = _load("kb.json")
CONFLUENCE = _load("confluence.json")
SERVICENOW = _load("servicenow.json")
JIRA       = _load("jira.json")


# Connector registry — drives the UI "Data Sources" panel and /api/sources.
SOURCES = [
    {"id": "kb",         "name": "Knowledge Base", "kind": "document",   "tool": "search_kb",
     "holds": "Runbooks, policy, standards",                "records": len(KB)},
    {"id": "confluence", "name": "Confluence",     "kind": "document",   "tool": "search_confluence",
     "holds": "Wiki: overview, architecture, FAQ, notes",   "records": len(CONFLUENCE)},
    {"id": "servicenow", "name": "ServiceNow",     "kind": "structured", "tool": "query_servicenow",
     "holds": "Incidents, requests, changes, CMDB, CIDR",   "records": sum(len(v) for v in SERVICENOW.values())},
    {"id": "jira",       "name": "Jira",           "kind": "structured", "tool": "query_jira",
     "holds": "Epics, features, stories, sprints",          "records": sum(len(v) for v in JIRA.values())},
]


_KB_INDEX   = retrieval.Index("kb",         KB,         "Knowledge Base")
_CONF_INDEX = retrieval.Index("confluence", CONFLUENCE, "Confluence")


def warmup():
    """Build both vector indexes up front (called on server startup)."""
    _KB_INDEX.build()
    _CONF_INDEX.build()


def retrieval_backend() -> str:
    """'vector' (Titan v2 + FAISS) or 'keyword' (fallback). For the UI/sources panel."""
    return retrieval.BACKEND


@tool
def search_kb(query: str) -> list:
    """Search the Knowledge Base: authoritative runbooks, policy, and standards.

    Use for: step-by-step procedures, policy requirements, change/freeze rules,
    decommission policy, CIDR standards. Semantic search over Titan-v2 embeddings.
    Returns cited snippets (e.g. 'Knowledge Base · Runbook/STEP-100'). Do NOT use
    for live ticket or CMDB state.
    """
    return _KB_INDEX.search(query)


@tool
def search_confluence(query: str) -> list:
    """Search Confluence wiki pages: process overview, reference architecture,
    the full step catalog, FAQs, and team meeting notes.

    Use for: orientation, "what are all the steps", architecture context, and
    recent team discussion. Semantic search over Titan-v2 embeddings. Returns cited
    snippets (e.g. 'Confluence · CLOUD/CLOUD-ARCH'). Confluence is collaborative and
    may lag the Knowledge Base — if it disagrees with KB or live state, flag the
    conflict rather than picking one silently.
    """
    return _CONF_INDEX.search(query)


@tool
def query_servicenow(table: str, key: str = "") -> dict:
    """Query ServiceNow systems-of-record for live, exact state. Authoritative for
    ticket and infrastructure state — always prefer this over documents for current values.

    table: one of incident, request, change_request, cmdb_ci_landing_zone, cidr_allocation.
    key:   optional filter matched against any field (e.g. an lz_id, team, number, or state).
    Returns the matching rows tagged with their source for citation.
    """
    rows = SERVICENOW.get(table, [])
    if key:
        k = key.lower()
        rows = [r for r in rows if k in json.dumps(r).lower()]
    return {"source": "ServiceNow", "table": table, "rows": rows}


@tool
def query_jira(item: str, key: str = "") -> dict:
    """Query Jira for live agile state. Authoritative for delivery progress —
    prefer this over documents for current feature/story/sprint status.

    item: one of epic, feature, story, sprint.
    key:  optional filter matched against any field (e.g. an lz_id, key, status, or sprint).
    Returns the matching rows tagged with their source for citation.
    """
    rows = JIRA.get(item, [])
    if key:
        k = key.lower()
        rows = [r for r in rows if k in json.dumps(r).lower()]
    return {"source": "Jira", "item": item, "rows": rows}


@tool
def validate_build_readiness(lz_id: str) -> dict:
    """Pre-flight readiness check for running the Vending Machine for a Landing Zone.

    Read-only. Inspects the ServiceNow CMDB and change records and returns a checklist:
      - the Landing Zone exists in the CMDB,
      - a non-overlapping CIDR is allocated for it,
      - a change request is approved/scheduled,
      - the order/CIDR pre-build steps are complete.
    Returns {lz_id, ready, checks:[{name, ok, detail}]}. 'ready' is True only if every
    check passes — the Vending Machine should not be proposed otherwise.
    """
    lz = next((c for c in SERVICENOW["cmdb_ci_landing_zone"]
               if c["lz_id"].lower() == lz_id.lower()), None)
    if not lz:
        return {"source": "ServiceNow", "lz_id": lz_id, "ready": False,
                "checks": [{"name": "CMDB record", "ok": False,
                            "detail": f"No CMDB CI found for {lz_id} — run intake/provisioning first"}]}

    checks = []

    cidr   = lz.get("cidr")
    cidr_ok = bool(cidr) and any(a["cidr"] == cidr for a in SERVICENOW["cidr_allocation"])
    checks.append({"name": "CIDR allocated", "ok": cidr_ok,
                   "detail": f"{cidr} recorded in CMDB" if cidr_ok else "No CIDR allocation found"})

    crq = next((c for c in SERVICENOW["change_request"]
                if c["lz_id"].lower() == lz_id.lower()), None)
    if crq:
        crq_ok = crq.get("approval") == "approved" or crq.get("state") in ("scheduled", "implement", "implemented")
        checks.append({"name": "Change request approved", "ok": crq_ok,
                       "detail": f"{crq['number']} state={crq['state']} approval={crq.get('approval')}"})
    else:
        checks.append({"name": "Change request approved", "ok": False,
                       "detail": "No change request found for this LZ (Step 300)"})

    step    = lz.get("current_step", 0)
    step_ok = step >= 100
    checks.append({"name": "Order & CIDR steps complete", "ok": step_ok,
                   "detail": f"current_step={step}"})

    ready = all(c["ok"] for c in checks)
    return {"source": "ServiceNow", "lz_id": lz_id, "team": lz.get("team"),
            "region": lz.get("region"), "ready": ready, "checks": checks}


@tool
def check_cidr(cidr: str) -> dict:
    """Check whether a candidate CIDR overlaps any block in the ServiceNow CMDB
    allocation registry. Read-only; safe to call freely.
    """
    try:
        net = ipaddress.ip_network(cidr, strict=False)
    except ValueError as e:
        return {"error": str(e)}
    allocated = [c["cidr"] for c in SERVICENOW.get("cidr_allocation", [])]
    conflicts = [c for c in allocated if net.overlaps(ipaddress.ip_network(c))]
    return {"source": "ServiceNow", "cidr": cidr,
            "available": not conflicts, "conflicts_with": conflicts}
