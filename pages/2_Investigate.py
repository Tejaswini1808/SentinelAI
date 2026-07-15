import streamlit as st

import ui_common

st.set_page_config(page_title="Investigate — SentinelAI", page_icon="🔍", layout="wide")
ui_common.bootstrap()

from app.agents.graph import run_alert_pipeline_with_progress  # noqa: E402
from app.store import store  # noqa: E402

st.title("🔍 Investigate")

alerts = sorted(store.list_alerts(), key=lambda a: a["id"], reverse=True)
if not alerts:
    st.warning("No alerts yet.")
    st.page_link("pages/1_Alerts.py", label="Go create or seed some alerts →")
    st.stop()

alert_labels = {a["id"]: f"{a['event_type']} — {a['description'][:60]} ({a['id'][:8]})" for a in alerts}
default_id = st.session_state.get("selected_alert_id", alerts[0]["id"])
selected_id = st.selectbox(
    "Select an alert",
    options=list(alert_labels.keys()),
    index=list(alert_labels.keys()).index(default_id) if default_id in alert_labels else 0,
    format_func=lambda i: alert_labels[i],
)
alert = store.get_alert(selected_id)

with st.expander("Raw alert", expanded=False):
    st.json(alert)

run = st.button("▶️ Run agent pipeline", type="primary")

if run:
    result_holder = {}

    def on_step(stage, state):
        result_holder["state"] = state
        if stage == "triage":
            classification = state["triage"].get("classification", "?")
            status.update(label=f"Triage complete — {classification}")
            if state["security_flags"]:
                st.toast(f"⚠️ {len(state['security_flags'])} security flag(s) raised during triage", icon="⚠️")
            if classification == "False Positive":
                status.update(label="Triage complete — False Positive, skipping investigation", state="complete")
        elif stage == "investigate":
            status.update(label="Investigation complete — generating incident report...")
        elif stage == "report":
            status.update(label="Incident report generated", state="complete")

    with st.status("Running Alert Triage Agent...", expanded=True) as status:
        final_state = run_alert_pipeline_with_progress(alert, on_step=on_step)

    classification = final_state.get("triage", {}).get("classification", "Medium")
    store.update_alert_status(
        selected_id, "closed_false_positive" if classification == "False Positive" else "investigated"
    )
    incident = store.add_incident(
        {
            "alert": alert,
            "triage": final_state.get("triage", {}),
            "investigation": final_state.get("investigation", {}),
            "report": final_state.get("report", {}),
            "grounding": final_state.get("grounding", {}),
            "security_flags": final_state.get("security_flags", []),
        }
    )
    st.session_state["last_incident_id"] = incident["id"]
    st.rerun()

incident_id = st.session_state.get("last_incident_id")
incident = store.get_incident(incident_id) if incident_id else None
if incident and incident["alert"]["id"] == selected_id:
    triage = incident["triage"]
    investigation = incident["investigation"]
    report = incident["report"]
    grounding = incident["grounding"]
    security_flags = incident["security_flags"]

    st.markdown("---")
    st.markdown(f"## Result: {ui_common.classification_badge(triage.get('classification', '?'))}", unsafe_allow_html=True)

    if security_flags:
        st.error(f"🚨 {len(security_flags)} security flag(s) raised (e.g. prompt injection in alert content)")
        with st.expander("Security flags"):
            st.json(security_flags)

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("**Triage rationale**")
        st.write(triage.get("rationale", "—"))
        st.markdown("**Matched MITRE techniques**")
        st.markdown(ui_common.chips(triage.get("matched_techniques", [])) or "—", unsafe_allow_html=True)
    with c2:
        st.metric("Confidence", f"{triage.get('confidence', 0):.0%}")
        if investigation:
            risk = investigation.get("risk", {})
            st.metric("Risk score", risk.get("risk_score", "—"))
            st.metric("CVSS estimate", risk.get("cvss_estimate", "—"))

    if investigation:
        st.markdown("### Investigation")
        t1, t2, t3, t4 = st.tabs(["Timeline", "Root cause & attack path", "Affected assets", "IOC enrichment"])
        with t1:
            for event in investigation.get("timeline", []):
                st.markdown(f"- `{event.get('time', '?')}` — {event.get('event', '')}")
        with t2:
            st.write("**Root cause:**", investigation.get("root_cause", "—"))
            st.write("**Attack path:**")
            for step in investigation.get("attack_path", []):
                st.markdown(f"- {step}")
        with t3:
            for asset in investigation.get("affected_assets", []):
                st.markdown(f"- {asset}")
        with t4:
            for ioc in investigation.get("ioc_enrichment", []):
                malicious = ioc.get("reputation", {}).get("malicious")
                badge_html = (
                    ui_common.badge("malicious", "critical", "🛑")
                    if malicious
                    else ui_common.badge("benign", "good", "🟢")
                )
                st.markdown(f"**{ioc['ioc']}** ({ioc['ioc_type']}) {badge_html}", unsafe_allow_html=True)
                st.json(ioc)

    if report:
        st.markdown("### Incident report")
        st.markdown(
            ui_common.grounding_badge(grounding.get("is_grounded", False), grounding.get("grounding_score", 0)),
            unsafe_allow_html=True,
        )
        rt1, rt2, rt3, rt4, rt5 = st.tabs(["Executive summary", "Technical summary", "Recommendations", "Playbook", "MITRE mapping"])
        rt1.write(report.get("executive_summary", "—"))
        rt2.write(report.get("technical_summary", "—"))
        with rt3:
            for r in report.get("recommendations", []):
                st.markdown(f"- {r}")
        with rt4:
            for i, step in enumerate(report.get("playbook", []), 1):
                st.markdown(f"{i}. {step}")
        with rt5:
            st.markdown(ui_common.chips(report.get("mitre_mapping", [])), unsafe_allow_html=True)
