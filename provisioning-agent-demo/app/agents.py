"""Supervisor + read specialists.

Read requests go to a specialist; provisioning and decommission
requests dispatch to a sequential pipeline of step agents (pipeline.py).
"""
from strands import Agent, tool

from .models import MODEL
from .tools import search_docs, query_state, check_cidr
from . import pipeline

GROUND = (
    "Answer only from tool results; if the answer is absent, say so plainly. "
    "When using documents, always cite the source and id (e.g. 'Runbook - STEP-100'). "
    "If two sources disagree on a value, present both and flag the conflict — never silently pick one. "
    "For live state (Landing Zone status, step progress, CIDR allocations, tickets) use query_state; "
    "it is authoritative and must be preferred over documentation for current values. "
    "Be concise and precise."
)


def _specialist(role: str, tools: list) -> Agent:
    return Agent(model=MODEL, system_prompt=f"{role}\n\n{GROUND}", tools=tools)


_docs      = _specialist("You are the Documentation and Process specialist. You answer questions about build steps, policy, standards, and runbooks.", [search_docs])
_inventory = _specialist("You are the Inventory specialist. You answer questions about live Landing Zone status, step progress, CIDR allocations, tickets, and pipelines.", [query_state, check_cidr])


@tool
def ask_docs(question: str) -> str:
    """Answer questions about build steps, policy, standards, and process runbooks."""
    return str(_docs(question))


@tool
def ask_inventory(question: str) -> str:
    """Answer questions about live Landing Zone state, step status, CIDR allocations, tickets, and pipelines."""
    return str(_inventory(question))


@tool
def run_provisioning(request: str) -> str:
    """Provision a new Landing Zone by running the full build pipeline:
    Step 10 (Intake) -> Step 100 (CIDR) -> Step 300 (Change Request) ->
    Step 400 (Vending Machine) -> Step 900 (QA) -> Step 1000 (Handoff).
    Each step hands off to the next. Write actions are staged for human approval.
    """
    return pipeline.run(pipeline.PROVISIONING, request)


@tool
def run_decommission(request: str) -> str:
    """Decommission a Landing Zone by running the decommission pipeline:
    Eligibility -> Impact Check -> Change Request.
    The change request is staged for human approval before any teardown.
    """
    return pipeline.run(pipeline.DECOMMISSION, request)


SUPERVISOR = (
    "You are the orchestrator for a cloud Landing Zone provisioning assistant. "
    "Route each request to exactly one tool using this logic: "
    "process steps, policy, standards, or how-to questions -> ask_docs; "
    "live LZ state, step progress, CIDR allocations, tickets, or pipelines -> ask_inventory; "
    "provision or build a new Landing Zone -> run_provisioning; "
    "decommission or tear down a Landing Zone -> run_decommission. "
    "The provisioning and decommission tools run a multi-step agent pipeline — "
    "each step is a specialist agent that hands off to the next. "
    "Never fabricate records. Write actions require human approval and are only proposed, never auto-executed. "
    "Relay results clearly, preserving any citations from specialist agents."
)


def build_supervisor() -> Agent:
    return Agent(
        model=MODEL,
        system_prompt=SUPERVISOR,
        tools=[ask_docs, ask_inventory, run_provisioning, run_decommission],
    )
