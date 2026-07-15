import pandas as pd
import plotly.express as px
import streamlit as st

import ui_common

st.set_page_config(page_title="Metrics — SentinelAI", page_icon="📊", layout="wide")
ui_common.bootstrap()

from app.metrics import metrics  # noqa: E402

st.title("📊 AI / Ops Metrics")

if st.button("🔄 Refresh"):
    st.rerun()

snapshot = metrics.snapshot()
timings = snapshot["timings"]
counters = snapshot["counters"]
tokens = snapshot["token_usage"]

ui_common.stat_row(
    [
        ("Retrieval calls", str(counters.get("retrieval_calls", 0)), ""),
        ("Prompt injections blocked", str(counters.get("prompt_injection_blocked", 0)), ""),
        ("Hallucinations flagged", str(counters.get("hallucination_flagged", 0)), ""),
        ("Tool calls denied", str(counters.get("tool_calls_denied", 0)), ""),
    ]
)

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Latency by stage (avg ms)**")
    if timings:
        df = pd.DataFrame(
            [{"stage": k, "avg_ms": v["avg_ms"], "p95_ms": v["p95_ms"], "count": v["count"]} for k, v in timings.items()]
        ).sort_values("avg_ms", ascending=True)
        fig = px.bar(df, x="avg_ms", y="stage", orientation="h", text="count", template="plotly_dark")
        fig.update_traces(texttemplate="n=%{text}", textposition="outside")
        st.plotly_chart(fig, width="stretch")
    else:
        st.caption("No agent/LLM calls recorded yet — run the pipeline on an alert first.")

with col2:
    st.markdown("**Token usage**")
    if tokens.get("total_tokens"):
        df = pd.DataFrame(
            [{"type": "prompt", "tokens": tokens["prompt_tokens"]}, {"type": "completion", "tokens": tokens["completion_tokens"]}]
        )
        fig = px.pie(df, names="type", values="tokens", template="plotly_dark", hole=0.5)
        st.plotly_chart(fig, width="stretch")
        st.caption(f"Total: {tokens['total_tokens']} tokens")
    else:
        st.caption("No token usage recorded yet.")

st.markdown("---")
st.markdown("**Raw counters**")
st.json(counters)

st.markdown("**Raw timings**")
st.json(timings)
