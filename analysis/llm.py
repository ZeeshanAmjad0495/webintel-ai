from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class AnalysisOutput:
    summary: str
    detected_changes: list[str]
    risk_flags: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def analyze_monitor_change(*, url: str, previous_content: str | None, current_content: str) -> AnalysisOutput:
    """Deterministic structured analysis stub; replace with a real LLM provider later."""

    changes: list[str] = []
    risk_flags: list[str] = []

    if previous_content is None:
        changes.append("initial_capture")
    elif previous_content == current_content:
        changes.append("no_textual_change")
    else:
        changes.append("content_changed")
        delta = len(current_content) - len(previous_content)
        if abs(delta) > 500:
            risk_flags.append("large_content_delta")
        if "password" in current_content.lower() or "credential" in current_content.lower():
            risk_flags.append("sensitive_keywords_detected")

    summary = (
        f"Analyzed monitor content for {url}. "
        f"Detected: {', '.join(changes)}. "
        f"Risk flags: {', '.join(risk_flags) if risk_flags else 'none'}."
    )

    return AnalysisOutput(summary=summary, detected_changes=changes, risk_flags=risk_flags)
