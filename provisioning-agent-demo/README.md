Landing Zone Provisioning Agent — Demo
A multi-agent assistant for cloud Landing Zone lifecycle management.
A supervisor routes each request to either a read specialist or a sequential pipeline
of step agents that hand off to one another. All data is synthetic — no real
infrastructure, credentials, or organisational data is included.

What it demonstrates
Multi-agent topology
Supervisor
├── Documentation specialist  — runbooks, policy, step guidance
├── Inventory specialist       — live LZ state, step progress, CIDRs, tickets
├── Provisioning pipeline      — 6 sequential step agents
│   ├── Step 10  : Intake & Order Validation
│   ├── Step 100 : CIDR Allocation
│   ├── Step 300 : Change Request          → approval gate
│   ├── Step 400 : Vending Machine          → approval gate
│   ├── Step 900 : QA & Validation
│   └── Step 1000: Handoff & Welcome
└── Decommission pipeline      — 3 sequential step agents
    ├── Eligibility Check
    ├── Impact Check
    └── Change Request                     → approval gate
Key properties
Hybrid retrieval — Runbooks and policy go through document search.
Live state (LZ status, step progress, CIDR allocations, tickets) goes through
exact structured queries against systems-of-record. Structured state is never
embedded in a vector store.
Human-in-the-loop approval gate — Consequential write actions (Change
Requests, Vending Machine execution, decommission CRQs) are staged as pending
proposals. Nothing executes until a human approves in the UI, and every approval
is recorded to an immutable audit log.
Deterministic orchestration — Pipeline order and supervisor routing are
explicit and auditable, which is necessary in regulated environments.

Project layout
app/
  agents.py    supervisor + read specialists
  pipeline.py  provisioning (6 steps) and decommission (3 steps) pipelines
  tools.py     hybrid retrieval tools + governed action tools
  models.py    shared Bedrock model instance
  config.py    model id and region (env vars)
  server.py    FastAPI app: /api/chat, approve, reject, audit
data/
  docs.json    synthetic runbook and policy documents (all 17 build steps)
  state.json   synthetic systems-of-record: LZ registry, step tracker, CIDR allocations, tickets
web/
  index.html   single-page chat UI with pipeline trace and approval cards

Setup
1. AWS authentication (IAM Identity Center / SSO)
bashaws configure sso          # enter your portal start URL, region, then pick account and role
aws sso login --profile <profile-name>
export AWS_PROFILE=<profile-name>
export AWS_REGION=us-east-1
2. Install
bashpython -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
3. Select a model
bash# Claude 3 Haiku — fast, works for demos
export BEDROCK_MODEL_ID=us.anthropic.claude-3-haiku-20240307-v1:0

# Claude Sonnet — sharper routing and step reasoning (recommended if access is granted)
export BEDROCK_MODEL_ID=us.anthropic.claude-3-5-sonnet-20241022-v2:0
The IAM role you assume needs bedrock:InvokeModel and bedrock:Converse.
4. Run
bashuvicorn app.server:app --reload
Open http://127.0.0.1:8000

Demo script
PromptWhat it showsWhat are all the steps in the LZ build process?Documentation specialist + step listingWhat's the build status of LZ-1002?Inventory specialist + step trackerProvision a new Landing Zone for Team Delta in us-east-1Full 6-agent pipeline; two approval gates (CRQ + VM)Can LZ-1003 be decommissioned?3-agent decommission pipeline; one approval gate
A provisioning request runs roughly eight model calls in sequence (supervisor + six
step agents), so expect several seconds. The pipeline trace in the UI makes the
wait legible — each numbered step shows what that agent did.

Updating with real process content
To reflect the actual build process, edit these two files on your work machine:
data/docs.json — add or update step entries. Each entry needs:
json{ "id": "STEP-XXX", "title": "Step XXX: ...", "source": "Runbook", "text": "..." }
Keep text to 2–4 sentences. The agent reasons and cites; it does not need verbatim doc content.
data/state.json — update the landing_zones, step_tracker, and cidr_allocations
tables with realistic (but synthetic) values to make inventory queries more meaningful.
app/pipeline.py — update the task field of each pipeline step with the specific
instruction that agent should follow. One focused sentence per step is enough.
Do not commit real infrastructure data, credentials, IAM ARNs, hostnames, ticket numbers,
or colleague names to any repository.

Moving to production
DemoProduction swapdata/docs.json local searchBedrock Knowledge Base Retrieve (OpenSearch Serverless)data/state.json flat fileAthena / direct API over real systems-of-record tablesIn-process session stateDynamoDB session storeStaged actions + UI approvalLambda-backed actions, approval keyed to RBAC role, audit tableSequential pipelineConditional graph (branching and parallel steps where appropriate)Claude HaikuClaude Sonnet
The agent topology, tool signatures, and approval gate pattern do not change
when making these swaps — only the tool implementations do.