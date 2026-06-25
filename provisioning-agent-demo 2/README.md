# Forge — Build Factory Bot

A multi-agent assistant for cloud Landing Zone lifecycle management. It answers
questions across four enterprise systems, runs guided build and decommission
flows, and stages every consequential action for human approval.

Built with **Strands Agents** on **Amazon Bedrock**. All data is synthetic.

## Components

| Layer | What we use |
|---|---|
| Chat UI | Single-page HTML/JS (no framework), served by FastAPI |
| Server / API | FastAPI (Python), Server-Sent Events for live progress |
| Agent framework | Strands Agents |
| Models | Claude **Sonnet 4.5** (routing + specialists) and **Haiku 4.5** (pipeline steps), on Amazon Bedrock |
| Knowledge base (RAG) | **Titan Text Embeddings V2** + in-process **FAISS** vector search (keyword fallback) |
| Data sources | Knowledge Base + Confluence (documents) · ServiceNow + Jira (structured) — synthetic |
| Memory | Entity + decision store (JSON), durable facts only |
| Governance | Human approval gate + audit log |

## Agents

- **Supervisor** — routes each request to one specialist, or fans out across several and synthesises one cited answer.
- **Source specialists** — Knowledge Base, Confluence, ServiceNow, Jira (one data source each, every claim cited).
- **Build & Vending Machine specialist** — runs a pre-flight readiness check, then stages the Vending Machine for approval.
- **Pipelines** — provisioning (6 sequential step agents) and decommission (3 step agents).

## Data sources

| Source | Type | Holds |
|---|---|---|
| Knowledge Base | document search | Runbooks, policy, standards |
| Confluence | document search | Overview, architecture, step catalog, FAQ, notes |
| ServiceNow | structured | Incidents, requests, change requests, CMDB, CIDR |
| Jira | structured | Epics, features, stories, sprints |

Documents (KB, Confluence) are retrieved by semantic vector search; structured
sources (ServiceNow, Jira) are exact lookups and are never embedded.

## Get started

**Prerequisites:** Python 3.10+ and an AWS account with Bedrock access to a Claude
model and a Titan embedding model.

```bash
# 1. Authenticate to AWS  (a profile auto-refreshes the token — avoids mid-session expiry)
aws sso login --profile <profile>
export AWS_PROFILE=<profile>          # Windows: $env:AWS_PROFILE="<profile>"
export AWS_REGION=us-east-1           # Windows: $env:AWS_REGION="us-east-1"

# 2. Install
python -m venv .venv
source .venv/bin/activate             # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Run
uvicorn app.server:app --port 8000    # if the port is busy, use --port 8010
```

Open **http://127.0.0.1:8000**.

Defaults are built in (model ids, region, embedding model); override via the
`BEDROCK_MODEL_ID`, `BEDROCK_FAST_MODEL_ID`, `BEDROCK_EMBED_MODEL_ID`, and
`AWS_REGION` environment variables if needed.

## Try it

| Prompt | Shows |
|---|---|
| What are all the steps in the LZ build process? | Knowledge base retrieval, cited |
| Full status of LZ-1002 across ServiceNow and Jira | Multi-agent fan-out + synthesis |
| How long does CIDR generation take? | Conflict flagging across sources |
| Is LZ-1002 ready to build? Run the Vending Machine if so | Readiness check → gated approval |
| Provision a new Landing Zone for Team Delta in us-east-1 | 6-agent pipeline, two approval gates |
| *(New Session)* What was I working on? | Cross-session memory |

## More docs

- [OVERVIEW.md](OVERVIEW.md) — plain-English tour of every file and the workflow.
- [BLUEPRINT.md](BLUEPRINT.md) — architecture and production roadmap.

All content under `data/` is fabricated for demonstration. Do not commit real
infrastructure data, credentials, ticket numbers, hostnames, or names.


"What's the status of LZ-1002, what's blocking it, and what does policy say about the next step?"

