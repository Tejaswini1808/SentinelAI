# SentinelAI — Multi-Agent Autonomous Security Operations Platform

A working MVP of an agentic SOC automation platform: alerts flow through a
LangGraph multi-agent pipeline (triage → investigation → incident report),
grounded by a RAG knowledge base in Qdrant, with prompt-injection detection,
tool-permission enforcement, and hallucination/grounding checks on every
generated answer.

## Architecture

```
Alert (API/synthetic generator)
      │
      ▼
Alert Triage Agent  ──search_qdrant──►  RAG (Qdrant + OpenRouter embeddings)
      │  (False Positive / Low / Medium / Critical)
      ▼ (skips below if False Positive)
Investigation Agent ──search_mitre / enrich_ioc──► RAG + mock IOC enrichment
      │  (timeline, root cause, attack path, affected assets, risk score)
      ▼
Incident Report Agent ──search_qdrant (on low grounding, retries)──► RAG
      │  (executive summary, technical summary, recommendations, playbook, MITRE mapping)
      ▼
Incident stored + returned via API
```

Cross-cutting guardrails (`app/security/`):
- **Prompt injection guard** — regex/heuristic scan on untrusted alert/user text before it reaches the LLM.
- **Tool permission guard** — each agent has an explicit allowlist of tools it may call (`app/security/tool_guard.py`); disallowed calls raise instead of silently no-op'ing.
- **Hallucination / grounding guard** — after generation, checks embedding-similarity between the answer and retrieved context plus explicit source citation; ungrounded incident reports trigger one retry with broader retrieval.

## Knowledge base

`app/data/knowledge_base.py` seeds ~70 documents into Qdrant: 45 MITRE ATT&CK
techniques, OWASP Top 10 (2021), NIST CSF functions, a handful of well-known
CVEs, synthetic SOC runbooks/policies, and synthetic past-incident reports.
Retrieval (`app/rag/retrieval.py`) does dense vector search over Qdrant plus a
keyword-overlap re-rank pass (a lightweight hybrid-search approximation).

## Setup

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Fill in `.env` (see `.env.example`) with your OpenRouter and Qdrant Cloud
credentials, then ingest the knowledge base:

```bash
python -m app.rag.ingest
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Generate synthetic alerts and run them through the full pipeline:

```bash
python ../scripts/generate_alerts.py --count 10 --investigate
```

### Notes on this environment

- If you're behind a TLS-inspecting corporate proxy (e.g. Zscaler), Python's
  `certifi` bundle won't trust its root CA even though `curl`/the OS does.
  `app/config.py` calls `truststore.inject_into_ssl()` to make Python use the
  OS trust store instead — this is required for the OpenRouter/Qdrant calls
  to work on such networks.
- OpenRouter's free-tier models (`:free` suffix) are globally rate-limited
  across all users and change availability over time. `app/llm/provider.py`
  retries across a configurable fallback list (`OPENROUTER_FALLBACK_MODELS`)
  rather than hardcoding one model.
- Qdrant Cloud free-tier clusters auto-pause when idle — if `python -m
  app.rag.ingest` times out connecting, resume the cluster from the Qdrant
  Cloud dashboard first.

## API

| Endpoint | Description |
|---|---|
| `POST /alerts` | Ingest a new alert |
| `GET /alerts` / `GET /alerts/{id}` | List / fetch alerts |
| `POST /investigate/{alert_id}` | Run the full triage → investigation → report pipeline |
| `GET /incident/{id}` / `GET /incidents` | Fetch generated incident report(s) |
| `POST /chat` | RAG-grounded Q&A over the security knowledge base |
| `POST /search` | Raw retrieval endpoint |
| `POST /agents/triage` / `/agents/hunt` / `/agents/report` | Invoke a single agent directly |
| `GET /metrics` | Retrieval latency, agent execution time, token usage, prompt-injection/hallucination counters |

## What's here vs. the full spec

This MVP implements 3 of the 6 planned agents (Triage, Investigation — which
also covers threat hunting, IOC enrichment, and risk scoring for now — and
Incident Report), an in-memory store instead of Postgres/Redis, and no
frontend yet. The event pipeline (NATS/Kafka), dashboard, and remaining
agent split-outs are natural next steps once this core loop is validated.
