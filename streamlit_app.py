import streamlit as st

import ui_common

st.set_page_config(page_title="SentinelAI", page_icon="🛰️", layout="wide")
ui_common.bootstrap()

from app.config import get_settings  # noqa: E402
from app.store import store  # noqa: E402

settings = get_settings()

st.title("🛰️ SentinelAI")
st.caption("Multi-Agent Autonomous Security Operations Platform")

if settings.demo_mode:
    st.info(
        "**Demo mode** — running on OpenRouter's free-tier models. Agent calls can take "
        "10–60s each since free models are globally rate-limited; the pipeline retries "
        "across a fallback list automatically. Set `VLLM_API_URL` to point at a self-hosted "
        "model instead.",
        icon="⚠️",
    )

col1, col2, col3, col4 = st.columns(4)
col1.metric("Alerts", len(store.list_alerts()))
col2.metric("Incidents", len(store.list_incidents()))
col3.metric("KB Collection", settings.qdrant_collection)
col4.metric("Mode", "Demo (OpenRouter)" if settings.demo_mode else "Self-hosted (vLLM)")

st.markdown("---")

st.markdown(
    """
### Architecture

```
Alert  →  Alert Triage Agent  →  Investigation Agent  →  Incident Report Agent
              │ (RAG: MITRE/OWASP/NIST/CVE/runbooks in Qdrant)
              ▼
        False Positive / Low / Medium / Critical
```

Every generated answer is checked for **prompt injection** before it reaches the LLM,
every agent tool call is checked against a **permission allowlist**, and every generated
report is checked for **grounding** against retrieved sources before being returned.
"""
)

st.markdown("### Get started")
c1, c2, c3 = st.columns(3)
with c1:
    st.page_link("pages/1_Alerts.py", label="🚨 Submit or seed alerts", icon="🚨")
with c2:
    st.page_link("pages/2_Investigate.py", label="🔍 Run the agent pipeline", icon="🔍")
with c3:
    st.page_link("pages/3_Chat.py", label="💬 Ask the security knowledge base", icon="💬")

c4, c5, c6 = st.columns(3)
with c4:
    st.page_link("pages/4_Security.py", label="🛡️ AI safety guardrails demo", icon="🛡️")
with c5:
    st.page_link("pages/5_Metrics.py", label="📊 AI/ops metrics", icon="📊")
with c6:
    st.page_link("pages/6_Knowledge_Base.py", label="📚 Browse the knowledge base", icon="📚")
