"""Post-hoc groundedness: verify the reply's citations actually exist.

"What happens when it's wrong?" — the most common failure for a cited assistant is
a *fabricated reference* (a confident citation to a doc/ticket that doesn't exist).
This checks every record id the reply mentions (KB/Confluence ids, ServiceNow
numbers and tables, Jira keys, LZ ids) against the real data and flags any that are
not found. It does not prove every sentence is supported — that is a fuller
groundedness/NLI check (roadmap) — but it catches hallucinated citations
deterministically, after generation, against the retrieval result (not just the
fact that a tool was called).
"""
import re

from . import sources

# Tokens that look like a cited record id.
_CITE = re.compile(
    r"\b(?:STEP-\d+[A-Z-]*|POLICY-[A-Z-]+|CLOUD-[A-Z0-9-]+|OVERVIEW"
    r"|INC-\d+|RITM-\d+|CRQ-\d+|FEAT-\d+|LZB-\d+|LZ-\d+"
    r"|cmdb_ci_landing_zone|change_request|cidr_allocation)\b"
)


def _known_ids() -> set:
    ids = set()
    for d in sources.KB:
        ids.add(d["id"])
    for d in sources.CONFLUENCE:
        ids.add(d["id"])

    sn = sources.SERVICENOW
    for table in ("incident", "request", "change_request"):
        for r in sn.get(table, []):
            ids.add(r.get("number"))
    for ci in sn.get("cmdb_ci_landing_zone", []):
        ids.add(ci.get("lz_id"))
    ids.update(["cmdb_ci_landing_zone", "change_request", "cidr_allocation", "incident", "request"])

    jira = sources.JIRA
    for kind in ("epic", "feature", "story"):
        for r in jira.get(kind, []):
            ids.add(r.get("key"))

    return {i for i in ids if i}


def verify_citations(reply: str) -> dict:
    """Return {checked, verified:[...], unverified:[...]} for ids referenced in `reply`."""
    known = _known_ids()
    found, seen = [], set()
    for tok in _CITE.findall(reply):
        if tok not in seen:
            seen.add(tok)
            found.append(tok)
    verified   = [t for t in found if t in known]
    unverified = [t for t in found if t not in known]
    return {"checked": len(found), "verified": verified, "unverified": unverified}
