"""Sequential build pipelines: one agent per step, executed in order with handoff context.

PROVISIONING — six sequential agents covering the key build gates:
  Step 10  : Intake & Order Validation
  Step 100 : CIDR Allocation
  Step 300 : Change Request (proposes for approval)
  Step 400 : Vending Machine Execution (proposes for approval)
  Step 900 : QA & Validation
  Step 1000: Handoff & Welcome

  Note: parallel pre-build steps (200 / 210 / 220) are surfaced within step agents
  as things to confirm are in-flight, not as separate sequential gates in this pipeline.

DECOMMISSION — three sequential agents:
  Eligibility  : confirms idle status and policy compliance
  Impact Check : identifies active dependencies
  Change Request: proposes the decommission CRQ for approval

TRACE records which agents ran so the UI can display the execution log.
"""
from strands import Agent

from .models import MODEL
from .tools import (
    search_docs, query_state, check_cidr,
    propose_change_request_lz, propose_vending_machine, propose_decommission,
)

TRACE: list = []

_RULES = (
    "Be concise — 2 to 4 sentences. Use only tool results; never invent records or state. "
    "You are one step in a build pipeline: complete your specific task, then pass context forward."
)


def _agent(role: str, tools: list) -> Agent:
    return Agent(model=MODEL, system_prompt=f"{role}\n\n{_RULES}", tools=tools)


PROVISIONING = [
    {
        "title": "Step 10 — Intake & Order Validation",
        "task": (
            "Verify the Landing Zone request is complete and ready to build. "
            "Check state for the LZ record: confirm the ITSM ticket ID, team name, region, "
            "and request type (new account, add account, or add application) are present. "
            "Confirm the Jira feature exists and the order files (parameter, metadata, feature, release) "
            "have been generated. Flag anything missing or inconsistent."
        ),
        "agent": _agent(
            "You are the Intake and Order Validation agent (build step 10). "
            "Your job is to confirm the Landing Zone order is complete and all prerequisites are met before the build begins.",
            [query_state, search_docs]
        ),
    },
    {
        "title": "Step 100 — CIDR Allocation",
        "task": (
            "Determine the CIDR allocation for the Landing Zone. "
            "Query the CIDR registry for current allocations and check that the assigned block does not overlap. "
            "If no CIDR is yet assigned, identify the next available non-overlapping block. "
            "State the CIDR clearly and note that production generation via the automation platform can take up to 30 minutes."
        ),
        "agent": _agent(
            "You are the CIDR Allocation agent (build step 100). "
            "Your job is to confirm or determine the non-overlapping CIDR block for the Landing Zone.",
            [query_state, check_cidr, search_docs]
        ),
    },
    {
        "title": "Step 300 — Change Request",
        "task": (
            "A Change Request must be submitted and approved before the Vending Machine executes. "
            "Check whether an active CRQ already exists in state for this Landing Zone. "
            "If one is needed, propose a Change Request summarising the LZ identifier, region, request type, "
            "and business justification. Note that the change window must be active at execution time and "
            "must not fall within a scheduled freeze window."
        ),
        "agent": _agent(
            "You are the Change Request agent (build step 300). "
            "Your job is to confirm an active Change Request exists, or propose one for human approval.",
            [query_state, search_docs, propose_change_request_lz]
        ),
    },
    {
        "title": "Step 400 — Vending Machine Execution",
        "task": (
            "This is the core build step. Summarise the Vending Machine execution plan for the Landing Zone: "
            "confirm the parameter file is ready, the compliance PR will be submitted, and whether the CMDB "
            "update will run coupled or decoupled (append the CMDB identifier to decouple). "
            "Confirm the Change Request from Step 300 is active. "
            "Propose the Vending Machine execution for human approval — this action provisions the environment."
        ),
        "agent": _agent(
            "You are the Vending Machine Execution agent (build step 400). "
            "Your job is to confirm readiness and propose the account vending machine execution for approval. "
            "This is the consequential build action — never claim it has run unless a tool confirmed success.",
            [query_state, propose_vending_machine]
        ),
    },
    {
        "title": "Step 900 — QA & Validation",
        "task": (
            "Review QA readiness for the Landing Zone. "
            "Confirm the three required validation checks: identity role federation, "
            "Terraform infrastructure boilerplate, and VPC endpoint configuration. "
            "Note that the observability check and Terraform plan check are known expected failures — "
            "they are normal and do not indicate defects. Any other failure must be documented. "
            "Check state for the current role and pipeline status. "
            "Remind: kinit must be run before the QA script, and the engineer must remove themselves "
            "from all LZ roles upon successful completion."
        ),
        "agent": _agent(
            "You are the QA and Validation agent (build step 900). "
            "Your job is to confirm the Landing Zone is ready for QA and describe what the validation checks.",
            [query_state, search_docs]
        ),
    },
    {
        "title": "Step 1000 — Handoff & Welcome",
        "task": (
            "Produce the final handoff summary for the owner team: "
            "Landing Zone ID, team, region, CIDR, request type, key steps completed, and any open post-build items "
            "(CICD onboarding, observability, monitoring, PAM). "
            "Note that a welcome meeting invitation must be sent and all ITSM tasks marked complete. "
            "Summarise what the team can expect to receive (welcome kit, account documentation page, access details)."
        ),
        "agent": _agent(
            "You are the Handoff and Welcome agent (build step 1000). "
            "Your job is to produce a clear, complete handoff summary for the Landing Zone owner team.",
            [query_state, search_docs]
        ),
    },
]

DECOMMISSION = [
    {
        "title": "Eligibility Check",
        "task": (
            "Check the Landing Zone's current status in state. "
            "Verify it meets the decommission policy: confirm it is marked idle, check the idle period, "
            "and look up the policy requirement for idle time before decommission is permitted. "
            "Flag if the environment does not meet the criteria."
        ),
        "agent": _agent(
            "You are the Decommission Eligibility agent. "
            "Your job is to confirm the Landing Zone qualifies for decommission under policy.",
            [query_state, search_docs]
        ),
    },
    {
        "title": "Impact Check",
        "task": (
            "Identify any active dependencies that would be affected by decommissioning this Landing Zone. "
            "Check state for active pipelines, open ITSM tickets, in-progress Jira features, "
            "and any resources still linked to this environment. "
            "Summarise what would be impacted."
        ),
        "agent": _agent(
            "You are the Decommission Impact agent. "
            "Your job is to identify all active dependencies before decommission proceeds.",
            [query_state]
        ),
    },
    {
        "title": "Change Request",
        "task": (
            "Propose a decommission Change Request citing the eligibility result and impact assessment above. "
            "This must be approved before any teardown actions can proceed. "
            "Include the Landing Zone ID, reason for decommission, and confirmation that eligibility criteria were met."
        ),
        "agent": _agent(
            "You are the Decommission Change Request agent. "
            "Your job is to stage the decommission change request for human approval.",
            [propose_decommission]
        ),
    },
]


def run(steps: list, request: str) -> str:
    """Execute a pipeline end to end, threading context between step agents."""
    context = f"Request: {request}"
    final   = ""
    for step in steps:
        prompt = f"{context}\n\nYour task ({step['title']}): {step['task']}"
        out    = str(step["agent"](prompt)).strip()
        TRACE.append({"agent": step["title"], "output": out})
        context += f"\n\n[{step['title']}] {out}"
        final    = out
    return final
