import streamlit as st

import ui_common

st.set_page_config(page_title="Alerts — SentinelAI", page_icon="🚨", layout="wide")
ui_common.bootstrap()

from app.store import store  # noqa: E402
from scripts.generate_alerts import generate  # noqa: E402

st.title("🚨 Alerts")

with st.expander("Submit a new alert", expanded=len(store.list_alerts()) == 0):
    with st.form("new_alert"):
        c1, c2 = st.columns(2)
        event_type = c1.text_input("Event type", value="suspicious_process")
        severity_hint = c2.selectbox("Severity hint", ["low", "medium", "high", "critical"], index=1)
        description = st.text_area(
            "Description",
            value="powershell.exe spawned from winword.exe with an encoded command line downloading a remote payload.",
        )
        c3, c4, c5 = st.columns(3)
        src_ip = c3.text_input("Source IP", value="10.0.4.22")
        dest_ip = c4.text_input("Destination IP", value="")
        user = c5.text_input("User", value="")
        source = st.selectbox("Source system", ["edr", "siem", "email_gateway", "firewall", "cloud_audit"])
        submitted = st.form_submit_button("Create alert", type="primary")

        if submitted:
            alert = {
                "event_type": event_type,
                "description": description,
                "severity_hint": severity_hint,
                "src_ip": src_ip or None,
                "dest_ip": dest_ip or None,
                "user": user or None,
                "source": source,
                "raw_log": f"[{source}] {description}",
            }
            record = store.add_alert(alert)
            st.success(f"Created alert {record['id']}")
            st.rerun()

st.markdown("Or seed a batch of synthetic alerts (including one crafted prompt-injection attempt):")
seed_count = st.slider("Number of synthetic alerts", 1, 15, 5)
if st.button("🌱 Seed demo alerts"):
    for alert in generate(seed_count):
        store.add_alert(alert)
    st.success(f"Seeded {seed_count} synthetic alerts")
    st.rerun()

st.markdown("---")
st.subheader(f"All alerts ({len(store.list_alerts())})")

alerts = sorted(store.list_alerts(), key=lambda a: a["id"], reverse=True)
if not alerts:
    st.caption("No alerts yet — submit one above or seed demo alerts.")
else:
    for alert in alerts:
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"**{alert['event_type']}** — {alert['description'][:120]}")
            c2.caption(f"status: `{alert['status']}`")
            c3.caption(f"id: `{alert['id'][:8]}`")
            if st.button("Investigate →", key=f"go_{alert['id']}"):
                st.session_state["selected_alert_id"] = alert["id"]
                st.switch_page("pages/2_Investigate.py")
