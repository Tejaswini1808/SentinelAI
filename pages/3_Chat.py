import streamlit as st

import ui_common

st.set_page_config(page_title="Chat — SentinelAI", page_icon="💬", layout="wide")
ui_common.bootstrap()

from app.chat_service import answer_question  # noqa: E402
from app.data.knowledge_base import build_knowledge_base  # noqa: E402

st.title("💬 Security Knowledge Assistant")
st.caption("RAG-grounded Q&A over MITRE ATT&CK, OWASP, NIST, CVEs, runbooks, and past incidents.")

source_types = sorted({d["source_type"] for d in build_knowledge_base()})
source_filter = st.selectbox("Filter by source type (optional)", ["(all)"] + source_types)
source_filter = None if source_filter == "(all)" else source_filter

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("meta"):
            meta = msg["meta"]
            st.markdown(
                ui_common.grounding_badge(
                    meta["grounding"].get("is_grounded", False), meta["grounding"].get("grounding_score", 0)
                ),
                unsafe_allow_html=True,
            )
            if meta["sources"]:
                with st.expander(f"{len(meta['sources'])} source(s)"):
                    for s in meta["sources"]:
                        st.markdown(f"**{s['title']}** (`{s['doc_id']}`, score {s['score']:.2f})")
                        st.caption(s["text"])

prompt = st.chat_input("Ask about MITRE ATT&CK, OWASP, NIST, CVEs, or try a prompt-injection attempt...")
if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving context and generating a grounded answer..."):
            result = answer_question(prompt, source_filter)
        st.markdown(result["answer"])
        if result["security"]["is_injection"]:
            st.error("🚨 Prompt injection detected — request blocked before reaching the LLM.")
            st.json(result["security"])
        else:
            st.markdown(
                ui_common.grounding_badge(
                    result["grounding"].get("is_grounded", False), result["grounding"].get("grounding_score", 0)
                ),
                unsafe_allow_html=True,
            )
            if result["sources"]:
                with st.expander(f"{len(result['sources'])} source(s)"):
                    for s in result["sources"]:
                        st.markdown(f"**{s['title']}** (`{s['doc_id']}`, score {s['score']:.2f})")
                        st.caption(s["text"])

    st.session_state.chat_history.append(
        {"role": "assistant", "content": result["answer"], "meta": result}
    )
