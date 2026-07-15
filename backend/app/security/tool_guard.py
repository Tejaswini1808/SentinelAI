"""Permission-aware tool execution: agents may only call tools on their
allowlist. Denied calls raise instead of silently no-op-ing, so a
misconfigured or manipulated agent can't quietly execute a disallowed action.
"""
from app.metrics import metrics

ALL_TOOLS = {
    "search_logs",
    "search_mitre",
    "search_qdrant",
    "enrich_ioc",
    "delete_logs",
    "execute_shell",
    "modify_permissions",
}

AGENT_TOOL_PERMISSIONS: dict[str, set[str]] = {
    "triage_agent": {"search_logs", "search_qdrant"},
    "investigation_agent": {"search_logs", "search_mitre", "search_qdrant", "enrich_ioc"},
    "report_agent": {"search_qdrant"},
}


class ToolPermissionError(PermissionError):
    pass


def check_permission(agent_name: str, tool_name: str) -> None:
    allowed = AGENT_TOOL_PERMISSIONS.get(agent_name, set())
    metrics.incr("tool_calls_total")
    if tool_name not in allowed:
        metrics.incr("tool_calls_denied")
        raise ToolPermissionError(f"{agent_name} is not permitted to call tool '{tool_name}'")
    metrics.incr("tool_calls_allowed")


def call_tool(agent_name: str, tool_name: str, fn, *args, **kwargs):
    check_permission(agent_name, tool_name)
    return fn(*args, **kwargs)
