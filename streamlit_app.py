import streamlit as st

import ui_common

st.set_page_config(page_title="SentinelAI", page_icon="🛰️", layout="wide")
ui_common.bootstrap()

from app.config import get_settings  # noqa: E402
from app.store import store  # noqa: E402

settings = get_settings()

ui_common.hero(
    "🛰️ SentinelAI",
    "Multi-Agent Autonomous Security Operations Platform",
    ["LangGraph multi-agent", "RAG-grounded", "Prompt-injection safe", "Tool-permissioned"],
)

if settings.demo_mode:
    st.info(
        "**Demo mode** — running on OpenRouter's free-tier models. Agent calls can take "
        "10–60s each since free models are globally rate-limited; the pipeline retries "
        "across a fallback list automatically. Set `VLLM_API_URL` to point at a self-hosted "
        "model instead.",
        icon="⚠️",
    )

incidents = store.list_incidents()
critical_count = sum(1 for i in incidents if i.get("triage", {}).get("classification") == "Critical")
mode_label = "Demo · OpenRouter" if settings.demo_mode else "Self-hosted · vLLM"

# Stat tiles are for magnitudes only (per the stat-tile contract) — identity
# strings like the collection name or mode go in a caption, not a tile.
ui_common.stat_row(
    [
        ("Alerts ingested", str(len(store.list_alerts())), ""),
        ("Incidents investigated", str(len(incidents)), ""),
        ("Critical incidents", str(critical_count), ""),
    ]
)
st.caption(f"Knowledge base: `{settings.qdrant_collection}` (Qdrant)  ·  Model mode: {mode_label}")

st.markdown("### Architecture")
with st.container(border=True):
    st.code(
        "Alert  ->  Alert Triage Agent  ->  Investigation Agent  ->  Incident Report Agent\n"
        "              | (RAG: MITRE/OWASP/NIST/CVE/runbooks in Qdrant)\n"
        "              v\n"
        "        False Positive / Low / Medium / Critical",
        language=None,
    )

st.markdown(
    "Every generated answer is checked for **prompt injection** before it reaches the LLM, "
    "every agent tool call is checked against a **permission allowlist**, and every generated "
    "report is checked for **grounding** against retrieved sources before being returned."
)

st.markdown("### Get started")
c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.markdown("#### 🚨 Alerts")
        st.caption("Submit a real alert or seed synthetic ones (including a crafted prompt-injection attempt).")
        st.page_link("pages/1_Alerts.py", label="Open Alerts →")
with c2:
    with st.container(border=True):
        st.markdown("#### 🔍 Investigate")
        st.caption("Run the triage → investigation → report pipeline with live step-by-step progress.")
        st.page_link("pages/2_Investigate.py", label="Open Investigate →")
with c3:
    with st.container(border=True):
        st.markdown("#### 💬 Chat")
        st.caption("Ask the RAG-grounded security knowledge assistant.")
        st.page_link("pages/3_Chat.py", label="Open Chat →")

c4, c5, c6 = st.columns(3)
with c4:
    with st.container(border=True):
        st.markdown("#### 🛡️ Security")
        st.caption("Interactively test the prompt-injection scanner and tool-permission matrix.")
        st.page_link("pages/4_Security.py", label="Open Security →")
with c5:
    with st.container(border=True):
        st.markdown("#### 📊 Metrics")
        st.caption("Retrieval latency, agent execution time, token usage, guardrail counters.")
        st.page_link("pages/5_Metrics.py", label="Open Metrics →")
with c6:
    with st.container(border=True):
        st.markdown("#### 📚 Knowledge Base")
        st.caption("Browse and semantically search MITRE/OWASP/NIST/CVE/runbook documents.")
        st.page_link("pages/6_Knowledge_Base.py", label="Open Knowledge Base →")
