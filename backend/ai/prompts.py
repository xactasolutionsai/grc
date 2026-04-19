"""
Prompt templates for AI endpoints.

Prompts are intentionally conservative and tell the model to return *only*
JSON matching a well-defined schema. Callers pair this with ``format="json"``
so the Ollama runtime enforces JSON-only output when possible.
"""

from __future__ import annotations

from string import Template

_NO_HALLUCINATION = (
    "If the input is insufficient to answer confidently, return the JSON with "
    "empty strings, empty arrays, or the most conservative enum value. "
    "Never invent specific product names, CVE IDs, regulation clauses, or "
    "statistics that are not clearly implied by the input."
)


RISK_SCENARIO_PROMPT = Template(
    """You are a senior cybersecurity risk expert working inside a GRC platform.
Given the short risk input below, produce a structured risk analysis.

Input: "$input"

$no_hallucination

Return ONLY a single JSON object matching EXACTLY this schema (no extra keys,
no prose, no markdown fences):
{
  "description": "one-paragraph professional risk description",
  "threat_scenario": "concise attack or failure scenario, 1-3 sentences",
  "impact": "business and technical impact, 1-3 sentences",
  "likelihood": {
    "level": "Low" | "Medium" | "High",
    "justification": "1-2 sentences explaining the level"
  },
  "risk_level": "Low" | "Medium" | "High" | "Critical",
  "recommended_mitigations": ["short actionable mitigation", "..."],
  "security_domains": ["e.g. Identity & Access", "Network Security", "..."]
}
"""
).safe_substitute(no_hallucination=_NO_HALLUCINATION)


EXPAND_TEXT_PROMPT = Template(
    """You are a GRC writing assistant. Expand the user's short input into a
clearer, professionally-written $field_type description. Keep the user's
intent and all concrete facts. Do not invent specifics.

User input: "$text"
$extra_context

$no_hallucination

Return ONLY a JSON object:
{"expanded": "the rewritten, expanded text"}
"""
)


GENERATE_CONTROLS_PROMPT = Template(
    """You are a security controls expert. Given the risk description below,
propose 3 to 6 relevant security controls. Favor well-known control types
(preventive, detective, corrective, deterrent, compensating).

Risk description: "$risk_description"

$no_hallucination

Return ONLY a JSON object:
{
  "controls": [
    {
      "name": "short control name",
      "description": "1-2 sentence description of what the control does",
      "implementation_guidance": "concrete steps to implement the control",
      "control_type": "preventive" | "detective" | "corrective" | "deterrent" | "compensating"
    }
  ]
}
"""
).safe_substitute(no_hallucination=_NO_HALLUCINATION)


GENERATE_FINDING_PROMPT = Template(
    """You are an audit finding writer. Turn the raw audit observation below
into a well-structured finding.

Observation: "$observation"

$no_hallucination

Return ONLY a JSON object:
{
  "title": "short finding title",
  "description": "clear description of the gap or issue",
  "impact": "why this matters, 1-2 sentences",
  "recommendation": "actionable remediation",
  "severity": "low" | "medium" | "high" | "critical"
}
"""
).safe_substitute(no_hallucination=_NO_HALLUCINATION)


DASHBOARD_INSIGHTS_PROMPT = Template(
    """You are a CISO assistant summarizing the state of a GRC program.
Analyze the anonymized statistics below and produce concise insights.

Statistics (JSON):
$stats

$no_hallucination

Return ONLY a JSON object:
{
  "top_risks": ["short bullet describing a notable risk area", "..."],
  "compliance_gaps": ["short bullet", "..."],
  "recommended_actions": ["short actionable recommendation", "..."],
  "summary": "3-5 sentence executive summary"
}
"""
).safe_substitute(no_hallucination=_NO_HALLUCINATION)


def render_risk_scenario_prompt(user_input: str) -> str:
    return Template(RISK_SCENARIO_PROMPT).safe_substitute(input=user_input.strip())


def render_expand_text_prompt(
    text: str, field_type: str, context: str | None = None
) -> str:
    extra = f'Context: "{context.strip()}"' if context else ""
    return EXPAND_TEXT_PROMPT.safe_substitute(
        text=text.strip(),
        field_type=field_type,
        extra_context=extra,
        no_hallucination=_NO_HALLUCINATION,
    )


def render_generate_controls_prompt(risk_description: str) -> str:
    return Template(GENERATE_CONTROLS_PROMPT).safe_substitute(
        risk_description=risk_description.strip()
    )


def render_generate_finding_prompt(observation: str) -> str:
    return Template(GENERATE_FINDING_PROMPT).safe_substitute(
        observation=observation.strip()
    )


def render_dashboard_insights_prompt(stats_json: str) -> str:
    return Template(DASHBOARD_INSIGHTS_PROMPT).safe_substitute(stats=stats_json)
