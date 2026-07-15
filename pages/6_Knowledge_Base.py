import streamlit as st

import ui_common

st.set_page_config(page_title="Knowledge Base — SentinelAI", page_icon="📚", layout="wide")
ui_common.bootstrap()

from app.data.knowledge_base import build_knowledge_base  # noqa: E402
from app.rag import retrieval  # noqa: E402

st.title("📚 Security Knowledge Base")

docs = build_knowledge_base()
by_source = {}
for d in docs:
    by_source.setdefault(d["source_type"], 0)
    by_source[d["source_type"]] += 1

cols = st.columns(len(by_source))
for col, (source, count) in zip(cols, sorted(by_source.items())):
    col.metric(source, count)

st.markdown("---")
query = st.text_input("Semantic search", placeholder="e.g. lateral movement over RDP")
source_filter = st.selectbox("Filter by source type", ["(all)"] + sorted(by_source.keys()))
source_filter = None if source_filter == "(all)" else source_filter

if query:
    with st.spinner("Searching Qdrant..."):
        results = retrieval.search(query, top_k=8, source_filter=source_filter)
    for r in results:
        with st.container(border=True):
            st.markdown(f"**{r['title']}** &nbsp; {ui_common.chip(r['source_type'])}", unsafe_allow_html=True)
            st.caption(r["text"])
            st.caption(f"vector_score={r['vector_score']:.3f} · keyword_score={r['keyword_score']:.2f} · rerank_score={r['rerank_score']:.3f}")
else:
    st.caption("Enter a query above, or browse all documents below.")
    for d in docs:
        if source_filter and d["source_type"] != source_filter:
            continue
        with st.expander(d["title"]):
            st.write(d["text"])
