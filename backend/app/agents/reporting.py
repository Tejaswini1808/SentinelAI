import logging

from app.agents.state import AlertState
from app.llm.json_utils import extract_json
from app.llm.provider import chat_completion
from app.metrics import metrics
from app.rag import retrieval
from app.security import hallucination_guard
from app.security.tool_guard import call_tool

logger = logging.getLogger(__name__)

AGENT_NAME = "report_agent"

SYSTEM_PROMPT = """You are the Incident Report Agent in a SOC automation platform.
Using the triage classification and investigation findings, produce a complete
incident report. Ground every claim in the provided context/findings — do not
invent details not supported by them.

Respond ONLY with JSON:
{
  "executive_summary": "...",
  "technical_summary": "...",
  "recommendations": ["..."],
  "playbook": ["..."],
  "mitre_mapping": ["T1566: Phishing", "..."]
}
"""


def _report_text(report: dict) -> str:
    return " ".join([report.get("executive_summary", ""), report.get("technical_summary", "")])


def _generate(alert: dict, triage: dict, investigation: dict, context: list[dict]) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"ALERT:\n{alert}\n\nTRIAGE:\n{triage}\n\nINVESTIGATION:\n{investigation}\n\n"
                f"SUPPORTING CONTEXT:\n" + "\n".join(f"- {c['title']}: {c['text']}" for c in context)
            ),
        },
    ]
    response = chat_completion(messages, metric_name="agent_time_report_llm", max_tokens=1536)
    result = extract_json(response["content"])
    result["_model"] = response["model"]
    return result


def report_node(state: AlertState) -> dict:
    with metrics.time_block("agent_time_report"):
        alert = state["alert"]
        triage = state.get("triage", {})
        investigation = state.get("investigation", {})
        context = state.get("retrieved_context", [])

        try:
            report = _generate(alert, triage, investigation, context)
        except Exception as exc:
            logger.exception("report LLM call failed")
            return {
                "report": {"executive_summary": f"Report generation failed: {exc}"},
                "grounding": {"is_grounded": False, "reason": "generation failed"},
            }

        grounding = hallucination_guard.check_grounding(_report_text(report), context)

        if not grounding["is_grounded"]:
            metrics.incr("hallucination_retry")
            extra_context = call_tool(
                AGENT_NAME,
                "search_qdrant",
                retrieval.search,
                query=f"{alert.get('event_type', '')} {triage.get('classification', '')}",
                top_k=8,
            )
            merged_context = context + [c for c in extra_context if c not in context]
            try:
                report = _generate(alert, triage, investigation, merged_context)
                grounding = hallucination_guard.check_grounding(_report_text(report), merged_context)
            except Exception as exc:
                logger.exception("report retry failed")
                grounding["reason"] = f"retry failed: {exc}"

        return {"report": report, "grounding": grounding}
