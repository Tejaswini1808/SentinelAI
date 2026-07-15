from langgraph.graph import END, START, StateGraph

from app.agents.investigation import investigation_node
from app.agents.reporting import report_node
from app.agents.state import AlertState
from app.agents.triage import triage_node


def _route_after_triage(state: AlertState) -> str:
    classification = state.get("triage", {}).get("classification", "Medium")
    if classification == "False Positive":
        return END
    return "investigate"


def build_graph():
    graph = StateGraph(AlertState)
    graph.add_node("triage", triage_node)
    graph.add_node("investigate", investigation_node)
    graph.add_node("report", report_node)

    graph.add_edge(START, "triage")
    graph.add_conditional_edges("triage", _route_after_triage, {"investigate": "investigate", END: END})
    graph.add_edge("investigate", "report")
    graph.add_edge("report", END)

    return graph.compile()


_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def run_alert_pipeline(alert: dict) -> AlertState:
    graph = get_graph()
    result = graph.invoke({"alert": alert})
    return result
