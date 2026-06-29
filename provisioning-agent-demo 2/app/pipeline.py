"""Sequential build pipelines: one agent per step, executed in order with handoff context.

PROVISIONING — six sequential agents covering the key build gates:
  Step 10  : Intake & Order Validation     (ServiceNow + Jira + KB)
  Step 100 : CIDR Allocation                (ServiceNow CMDB + KB)
  Step 300 : Change Request                 (ServiceNow + KB) → approval gate
  Step 400 : Vending Machine Execution      (ServiceNow) → approval gate
  Step 900 : QA & Validation                (ServiceNow + KB)
  Step 1000: Handoff & Welcome              (ServiceNow + KB)

DECOMMISSION — three sequential agents:
  Eligibility  : ServiceNow CMDB + KB policy
  Impact Check : ServiceNow + Jira
  Change Request: → approval gate

TRACE records which agent ran, what it produced, and which data sources it was
wired to — so the UI can show the fan-out, not just the order.
"""
from strands import Agent

from .models import FAST_MODEL
from .sources import search_kb, search_confluence, query_servicenow, query_jira, check_cidr
from .actions import propose_change_request_lz, propose_vending_machine, propose_decommission
from .config import FAST_MODEL_LABEL
from . import events

TRACE: list = []

_RULES = (
    "Be concise — 2 to 4 sentences. Use only tool results; never invent records or state. "
    "Cite the source connector for live values (ServiceNow / Jira) and for any policy (Knowledge Base). "
    "You are one step in a build pipeline: complete your specific task, then pass context forward."
)


def _agent(role: str, tools: list) -> Agent:
    # Step agents run on the fast (Haiku) model — many calls, tightly scripted tasks.
    return Agent(model=FAST_MODEL, system_prompt=f"{role}\n\n{_RULES}", tools=tools)


PROVISIONING = [
    {
        "title": "Step 10 — Intake & Order Validation",
        "sources": ["ServiceNow", "Jira", "Knowledge Base"],
        "task": (
            "Verify the Landing Zone request is complete and ready to build. "
            "Check the ServiceNow request (RITM) and CMDB record for the LZ: confirm team, region, and request type. "
            "Confirm the Jira feature exists and its story breakdown is underway. "
            "Flag anything missing or inconsistent."
        ),
        "agent": _agent(
            "You are the Intake and Order Validation agent (build step 10). "
            "You confirm the Landing Zone order is complete across ServiceNow and Jira before the build begins.",
            [query_servicenow, query_jira, search_kb]
        ),
    },
    {
        "title": "Step 100 — CIDR Allocation",
        "sources": ["ServiceNow CMDB", "Knowledge Base"],
        "task": (
            "Determine the CIDR allocation for the Landing Zone. "
            "Query the ServiceNow CMDB CIDR registry for current allocations and check the assigned block does not overlap. "
            "If no CIDR is yet assigned, identify the next available non-overlapping block. "
            "State the CIDR clearly and cite the KB CIDR standard."
        ),
        "agent": _agent(
            "You are the CIDR Allocation agent (build step 100). "
            "You confirm or determine the non-overlapping CIDR block from the ServiceNow CMDB.",
            [query_servicenow, check_cidr, search_kb]
        ),
    },
    {
        "title": "Step 300 — Change Request",
        "sources": ["ServiceNow", "Knowledge Base"],
        "task": (
            "A standard (pre-approved) change must authorize the build before the Vending Machine executes. "
            "Check ServiceNow for an existing CRQ for this Landing Zone and its state. "
            "If one is needed, propose a standard Change Request summarising the LZ identifier, region, request type, "
            "and business justification. Per KB policy, the CIDR blocks (Step 100) must exist before the "
            "implementation start date; standard changes need only assignment and scheduling, not extra approvals."
        ),
        "agent": _agent(
            "You are the Change Request agent (build step 300). "
            "You confirm an active ServiceNow CRQ exists, or propose one for human approval.",
            [query_servicenow, search_kb, propose_change_request_lz]
        ),
    },
    {
        "title": "Step 400 — Vending Machine Execution",
        "sources": ["ServiceNow"],
        "task": (
            "This is the core build step. Summarise the Vending Machine execution plan: confirm the per-account "
            "parameter files are ready and peer-reviewed, that CMDB updates will be triggered via the '-cmdb' "
            "execution-name suffix, and that the compliance-policy PR will follow. Confirm the ServiceNow change "
            "from Step 300 is scheduled/active. Propose the Vending Machine execution for human approval — this "
            "action provisions the environment."
        ),
        "agent": _agent(
            "You are the Vending Machine Execution agent (build step 400). "
            "You confirm readiness and propose the account vending machine execution for approval. "
            "This is the consequential build action — never claim it has run unless a tool confirmed success.",
            [query_servicenow, propose_vending_machine]
        ),
    },
    {
        "title": "Step 900 — QA & Validation",
        "sources": ["ServiceNow", "Knowledge Base"],
        "task": (
            "Review QA readiness. Per the KB runbook, the QA automation script validates role access, compliance "
            "contexts, CMDB relationships, network/CIDR assignments, and tool integrations. Note that for CICD-type "
            "landing zones only the observability (ELMA) and Terraform-plan checks are expected to fail — any other "
            "failure is a real defect. Check the ServiceNow CMDB for current step/status, and remind that the "
            "engineer must remove themselves from all LZ roles on successful completion."
        ),
        "agent": _agent(
            "You are the QA and Validation agent (build step 900). "
            "You confirm the Landing Zone is ready for QA and describe what the validation checks.",
            [query_servicenow, search_kb]
        ),
    },
    {
        "title": "Step 1000 — Handoff & Welcome",
        "sources": ["ServiceNow", "Knowledge Base"],
        "task": (
            "Produce the final handoff summary for the owner team: "
            "Landing Zone ID, team, region, CIDR, request type, key steps completed, and any open post-build items "
            "(CICD onboarding, observability, monitoring, privileged access). "
            "Note that the 30-minute welcome meeting (led by the customer engagement team) must be scheduled and the "
            "ServiceNow Quality Inspection task closed to mark the LZ delivered. "
            "Summarise what the team receives (welcome kit, account documentation page, access details)."
        ),
        "agent": _agent(
            "You are the Handoff and Welcome agent (build step 1000). "
            "You produce a clear, complete handoff summary for the Landing Zone owner team.",
            [query_servicenow, search_kb]
        ),
    },
]

DECOMMISSION = [
    {
        "title": "Eligibility Check",
        "sources": ["ServiceNow CMDB", "Knowledge Base"],
        "task": (
            "Check the Landing Zone's current status in the ServiceNow CMDB. "
            "Verify it meets the KB decommission policy: confirm it is idle, check the idle period against the "
            "policy minimum, and flag if it does not qualify."
        ),
        "agent": _agent(
            "You are the Decommission Eligibility agent. "
            "You confirm the Landing Zone qualifies for decommission under Knowledge Base policy.",
            [query_servicenow, search_kb]
        ),
    },
    {
        "title": "Impact Check",
        "sources": ["ServiceNow", "Jira"],
        "task": (
            "Identify active dependencies that would be affected by decommissioning this Landing Zone. "
            "Check ServiceNow for open tickets and the CMDB, and Jira for in-progress features or stories tied "
            "to this environment. Summarise what would be impacted."
        ),
        "agent": _agent(
            "You are the Decommission Impact agent. "
            "You identify all active dependencies across ServiceNow and Jira before decommission proceeds.",
            [query_servicenow, query_jira]
        ),
    },
    {
        "title": "Change Request",
        "sources": ["ServiceNow"],
        "task": (
            "Propose a decommission Change Request citing the eligibility result and impact assessment above. "
            "This must be approved before any teardown. Include the Landing Zone ID, reason, and confirmation "
            "that eligibility criteria were met."
        ),
        "agent": _agent(
            "You are the Decommission Change Request agent. "
            "You stage the decommission ServiceNow CRQ for human approval.",
            [propose_decommission]
        ),
    },
]


def run(steps: list, request: str) -> str:
    """Execute a pipeline end to end, threading context between step agents."""
    context = f"Request: {request}"
    final   = ""
    total   = len(steps)
    for i, step in enumerate(steps, 1):
        events.emit({"type": "step_start", "name": step["title"], "sources": step["sources"],
                     "index": i, "total": total, "model": FAST_MODEL_LABEL})
        prompt = f"{context}\n\nYour task ({step['title']}): {step['task']}"
        out    = str(step["agent"](prompt)).strip()
        events.emit({"type": "step_end", "name": step["title"], "output": out[:280]})
        TRACE.append({"agent": step["title"], "sources": step["sources"], "output": out})
        context += f"\n\n[{step['title']}] {out}"
        final    = out
    return final
