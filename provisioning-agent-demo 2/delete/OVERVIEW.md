# Overview — In Plain Terms

A team chatbot that answers questions from **four pretend company systems**
(Knowledge Base, Confluence, ServiceNow, Jira) and can run a **step-by-step build
or teardown** of a cloud "Landing Zone." It uses **multiple AI agents** that each
specialise in one system, **remembers** what you worked on, and **asks a human to
approve** anything risky. All data is fake.

---

## What every file and folder does

### `app/` — the brains (Python)

| File | In one sentence |
|---|---|
| `config.py` | Settings: which Claude model, which AWS region, which embedding model — read from environment variables. |
| `models.py` | Creates the shared Claude model (on AWS Bedrock) that every agent uses to think. |
| `sources.py` | **The four data connectors.** Defines `search_kb`, `search_confluence`, `query_servicenow`, `query_jira`, `check_cidr` — the only ways the bot can fetch information. |
| `embeddings.py` | Turns text into number-vectors using Amazon Titan, so the Knowledge Base and Confluence can be searched by *meaning*, not just keywords. |
| `retrieval.py` | The little search engine: builds a FAISS index of those vectors and finds the most relevant docs. Falls back to keyword search if AWS isn't reachable. |
| `actions.py` | **Risky actions.** Staging area for things that change the world (raise a change request, run the build, decommission). Nothing runs until a human clicks Approve; approved actions go to an audit log. |
| `agents.py` | **The team of agents.** A "supervisor" that decides who answers, one specialist per data source, and a Build & Vending Machine specialist that checks readiness before staging the build. |
| `pipeline.py` | **The assembly lines.** The 6-step "provision a Landing Zone" flow and the 3-step "decommission" flow. Each step is its own agent that hands off to the next. |
| `memory.py` | **Long-term memory.** Remembers *which* things you worked on and *what you decided* — but never live status (that's always looked up fresh, so memory can't go stale). |
| `events.py` | **Live progress.** Lets the bot report what it's doing in real time (routing, consulting a source, running a step, staging an action) so the screen updates as it works. |
| `guardrails.py` | **Safety filter.** Blocks bad input (prompt-injection, pasted secrets) and redacts secrets/PII from answers. |
| `grounding.py` | **Citation check.** After an answer, verifies every record it cited actually exists in the data — catches made-up references. |
| `server.py` | The web server (FastAPI). Wires everything together and streams the live progress to the web page (`/api/chat/stream`, approve/reject, memory). |
| `__init__.py` | Empty file that makes `app/` a Python package. |

### `data/` — the fake company data (JSON)

| File | What's inside |
|---|---|
| `kb.json` | **Knowledge Base** articles: runbooks, policies, standards. |
| `confluence.json` | **Confluence** wiki pages: overview, architecture, full step list, FAQ, meeting notes. |
| `servicenow.json` | **ServiceNow** records: incidents, requests, change requests, the CMDB (list of Landing Zones), and CIDR network allocations. |
| `jira.json` | **Jira** records: epics, features, stories, sprints. |
| `memory.json` | What the bot currently remembers (auto-updated as you chat). |
| `.embeddings_cache.json` | Auto-created. Saved vectors so it doesn't re-embed on every restart. (Git-ignored.) |

### `web/` — the screen

| File | What it does |
|---|---|
| `index.html` | The whole chat interface in one file: the chat window, the live activity panel, the left sidebar (memory + audit log), and the approve/reject buttons. |

### Top-level files

| File | What it does |
|---|---|
| `README.md` | Setup + how to run. |
| `BLUEPRINT.md` | The detailed architecture/design write-up. |
| `OVERVIEW.md` | This file — the plain-English tour. |
| `requirements.txt` | The Python packages to install. |
| `.gitignore` | Files Git should ignore. |

---

## How it works (the workflow)

```
You type a question in the web page
        │
        ▼
server.py  →  adds remembered context, sends it to the SUPERVISOR agent
        │
        ▼
SUPERVISOR (agents.py) decides what kind of question this is:
        │
        ├── a fact question  → asks one or more SPECIALIST agents
        │        (KB · Confluence · ServiceNow · Jira)
        │        each specialist calls its tool in sources.py to fetch data,
        │        then answers WITH A CITATION ("ServiceNow · CMDB", etc.)
        │
        ├── "is LZ-XXXX ready to build?" → the BUILD agent runs a readiness
        │        checklist, then STAGES the Vending Machine for approval
        │
        └── a "build" or "decommission" request → runs a PIPELINE (pipeline.py)
                 step 1 agent → step 2 agent → ... each handing off context,
                 pausing at risky steps to STAGE an action (actions.py)
        │
        ▼
As it works, the bot STREAMS live progress to the page (events.py) — routing,
each source consulted, each step, each action staged. Then it sends the final
answer, any pending approvals, and updated memory.
        │
        ▼
Web page shows a live activity panel + the answer.
        If there's a risky action, you see Approve / Reject buttons.
        Approving runs it and logs it to the audit trail.
```

**Four things to notice while it runs:**
1. **Live activity** — the panel ticks through each agent/step in real time as it happens.
2. **Multiple agents** — it shows which agent ran and which data source it used.
3. **Citations** — every fact says where it came from; if two sources disagree, the bot flags it.
4. **Memory** — the sidebar shows what it remembers; it carries over to your next session.

---

## How to run it

```bash
# 1. Log in to AWS (a profile auto-refreshes the token, so it won't expire mid-session)
aws sso login --profile <your-profile>
export AWS_PROFILE=<your-profile>     # Windows: $env:AWS_PROFILE="<your-profile>"
export AWS_REGION=us-east-1           # Windows: $env:AWS_REGION="us-east-1"

# 2. Install
python -m venv .venv
source .venv/bin/activate             # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Start it  (default model is Claude Sonnet 4.5; if the port is busy use --port 8010)
uvicorn app.server:app --port 8000
```

Open **http://127.0.0.1:8000**.

> If your AWS token expires, the bot returns an "ExpiredToken" error — re-login and
> restart the server. Using a profile (above) avoids this.

---

## How to test it (quick check)

Two layers:

- **Logic test (no AWS needed):** the connectors, search, and memory have been
  exercised with a stubbed model — they return the right citations and memory stays
  consistent. To re-verify the plumbing compiles: `python -m py_compile app/*.py`.
- **Full test (needs AWS):** run the server and use the demo prompts below. Confirm
  each answer carries a citation, the trace shows the expected agents, and approvals
  land in the Audit Log.

---

## How to demo it (5-minute script)

Click the suggestion chips, or type these in order:

| # | Type this | What to point at |
|---|---|---|
| 1 | **What are all the steps in the LZ build process?** | Answer comes from the **Knowledge Base / Confluence** step catalog, cited. |
| 2 | **Full status of LZ-1002 across ServiceNow and Jira** | Trace shows the supervisor **fanning out to two systems** and merging — one answer, two citations. |
| 3 | **How long does CIDR generation take?** | The bot **flags a conflict**: the Knowledge Base says up to ~20 min, a Confluence note says ~10 min. It won't silently pick one. |
| 4 | **Is LZ-1002 ready to build? Run the Vending Machine if so** | The **Build agent** runs a readiness checklist, then stages the Vending Machine for **approval**. |
| 5 | **Provision a new Landing Zone for Team Delta in us-east-1** | A **6-agent pipeline** runs step by step; two **Approve/Reject** cards appear. Approve them and watch the **Audit Log** fill. |
| 6 | **Can LZ-1003 be decommissioned?** | A **3-agent** teardown pipeline; one approval gate. |
| 7 | Click **New Session**, then ask **What was I working on?** | **Memory** recalls LZ-1002 / LZ-1003 and past decisions — but live status is re-fetched fresh. |

**The one-line pitch:** *"Multiple specialist agents answer from four enterprise
systems with citations, remember context across sessions, and never take a risky
action without a human in the loop — all on AWS Bedrock."*
