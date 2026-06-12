"""Supervisor + one specialist agent per data source.

Topology:
    Supervisor
    ├── ask_kb          → Knowledge Base specialist   (runbooks, policy, standards)
    ├── ask_confluence  → Confluence specialist        (overview, architecture, FAQ, notes)
    ├── ask_servicenow  → ServiceNow specialist        (incidents, requests, changes, CMDB, CIDR)
    ├── ask_jira        → Jira specialist              (epics, features, stories, sprints)
    ├── ask_build       → Build & Vending Machine spec. (pre-flight readiness check → gated VM proposal)
    ├── run_provisioning→ 6-step build pipeline        (pipeline.py)
    └── run_decommission→ 3-step decommission pipeline (pipeline.py)

For a read question the supervisor may consult ONE source, or fan out to SEVERAL
and synthesise a single cited answer. Each specialist only sees its own source,
so every claim is traceable to the system it came from.
"""
from strands import Agent, tool

from .models import MODEL
from .sources import (
    search_kb, search_confluence, query_servicenow, query_jira, check_cidr,
    validate_build_readiness,
)
from .actions import propose_vending_machine
from . import pipeline, events

GROUND = (
    "Answer only from tool results; if the answer is absent, say so plainly. "
    "Always cite the source connector and id for every claim (e.g. 'Knowledge Base · Runbook/STEP-100', "
    "'ServiceNow · cmdb_ci_landing_zone', 'Jira · FEAT-1002'). "
    "Live state (tickets, CMDB, CIDR, sprint/issue status) comes from ServiceNow and Jira and is authoritative; "
    "documents (Knowledge Base, Confluence) describe process and policy, not current values. "
    "If two sources disagree on a value, present both and flag the conflict explicitly — never silently pick one. "
    "Be concise and precise."
)


def _specialist(role: str, tools: list) -> Agent:
    return Agent(model=MODEL, system_prompt=f"{role}\n\n{GROUND}", tools=tools)


_kb         = _specialist("You are the Knowledge Base specialist. You answer from authoritative runbooks, policy, and standards.", [search_kb])
_confluence = _specialist("You are the Confluence specialist. You answer from wiki pages: process overview, reference architecture, the step catalog, FAQs, and meeting notes.", [search_confluence])
_servicenow = _specialist("You are the ServiceNow specialist. You answer from live records: incidents, requests, change requests, the Landing Zone CMDB, and CIDR allocations.", [query_servicenow, check_cidr])
_jira       = _specialist("You are the Jira specialist. You answer from live agile state: epics, features, stories, and sprints.", [query_jira])

_build = Agent(
    model=MODEL,
    system_prompt=(
        "You are the Build & Vending Machine specialist (build step 400). "
        "When asked to run, execute, or check readiness for the Vending Machine for a Landing Zone:\n"
        "1. ALWAYS call validate_build_readiness(lz_id) first to run the pre-flight checklist "
        "(CIDR allocated, change request approved/scheduled, order steps complete).\n"
        "2. Report the checklist clearly, item by item, citing 'ServiceNow'.\n"
        "3. ONLY if every check passes, call propose_vending_machine to stage the execution for human "
        "approval, and note that CMDB updates are triggered via the '-cmdb' execution-name suffix.\n"
        "4. If any check fails, explain exactly what must be resolved and DO NOT propose the action.\n"
        "Never claim the Vending Machine has run — it executes only after a human approves the proposal.\n\n"
        + GROUND
    ),
    tools=[query_servicenow, validate_build_readiness, propose_vending_machine],
)


def _consult(name: str, source: str, agent: Agent, question: str) -> str:
    events.emit({"type": "agent_start", "name": name, "source": source})
    out = str(agent(question))
    events.emit({"type": "agent_end", "name": name})
    return out


@tool
def ask_kb(question: str) -> str:
    """Knowledge Base: authoritative runbooks, policy, standards, change/freeze and decommission policy, CIDR standards."""
    return _consult("Knowledge Base specialist", "Knowledge Base", _kb, question)


@tool
def ask_confluence(question: str) -> str:
    """Confluence: process overview, reference architecture, the full step catalog, FAQs, and recent team meeting notes."""
    return _consult("Confluence specialist", "Confluence", _confluence, question)


@tool
def ask_servicenow(question: str) -> str:
    """ServiceNow: live incidents, requests (RITM), change requests (CRQ), the Landing Zone CMDB, and CIDR allocations."""
    return _consult("ServiceNow specialist", "ServiceNow", _servicenow, question)


@tool
def ask_jira(question: str) -> str:
    """Jira: live epics, features, stories, and sprint status for Landing Zone delivery."""
    return _consult("Jira specialist", "Jira", _jira, question)


@tool
def ask_build(request: str) -> str:
    """Build & Vending Machine specialist for an already-prepared Landing Zone (by lz_id).
    Runs the pre-flight readiness checklist (CIDR, change request, order steps) against ServiceNow,
    and if everything passes, stages the Vending Machine execution for human approval.
    Use for: 'validate build readiness', 'is LZ-XXXX ready to build', 'run/execute the Vending Machine for LZ-XXXX'.
    """
    return _consult("Build & Vending Machine specialist", "ServiceNow", _build, request)


@tool
def run_provisioning(request: str) -> str:
    """Provision a new Landing Zone by running the full build pipeline:
    Step 10 (Intake) -> Step 100 (CIDR) -> Step 300 (Change Request) ->
    Step 400 (Vending Machine) -> Step 900 (QA) -> Step 1000 (Handoff).
    Each step hands off to the next and reads from the relevant data source.
    Write actions are staged for human approval.
    """
    events.emit({"type": "pipeline_start", "name": "Provisioning pipeline",
                 "steps": len(pipeline.PROVISIONING)})
    return pipeline.run(pipeline.PROVISIONING, request)


@tool
def run_decommission(request: str) -> str:
    """Decommission a Landing Zone by running the decommission pipeline:
    Eligibility -> Impact Check -> Change Request.
    The change request is staged for human approval before any teardown.
    """
    events.emit({"type": "pipeline_start", "name": "Decommission pipeline",
                 "steps": len(pipeline.DECOMMISSION)})
    return pipeline.run(pipeline.DECOMMISSION, request)


SUPERVISOR = (
    "You are the orchestrator for a cloud Landing Zone assistant backed by four data sources: "
    "Knowledge Base (runbooks/policy), Confluence (wiki/overview/architecture/notes), "
    "ServiceNow (incidents/requests/changes/CMDB/CIDR), and Jira (epics/features/stories/sprints). "
    "Routing: "
    "process/policy/how-to/standards -> ask_kb; "
    "orientation, architecture, the full step catalog, FAQs, or team discussion -> ask_confluence; "
    "live tickets, change requests, Landing Zone CMDB state, or CIDR allocations -> ask_servicenow; "
    "feature/story/sprint/delivery status -> ask_jira; "
    "check build readiness, or run/execute the Vending Machine for an already-prepared Landing Zone "
    "named by its lz_id (e.g. 'is LZ-1002 ready to build', 'run the vending machine for LZ-1002') -> ask_build; "
    "provision or build a NEW Landing Zone end to end (no existing lz_id) -> run_provisioning; "
    "decommission or tear down a Landing Zone -> run_decommission. "
    "When a question spans systems (e.g. 'what's the status of LZ-1002 and what's left to do'), "
    "consult MULTIPLE source tools and synthesise ONE answer that cites each source used. "
    "The provisioning and decommission tools run a multi-step agent pipeline — each step is a "
    "specialist agent that hands off to the next. "
    "Never fabricate records. Write actions require human approval and are only proposed, never auto-executed. "
    "Preserve the citations returned by each specialist."
)


def build_supervisor() -> Agent:
    return Agent(
        model=MODEL,
        system_prompt=SUPERVISOR,
        tools=[ask_kb, ask_confluence, ask_servicenow, ask_jira, ask_build,
               run_provisioning, run_decommission],
    )
