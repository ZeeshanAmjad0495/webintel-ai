"""Concrete analyzer implementations."""

from __future__ import annotations

from typing import Any


class DeterministicAnalyzer:
    """Simple deterministic analyzer backed by local heuristic logic."""

    async def analyze(self, payload: dict[str, object]) -> dict[str, Any]:
        url = str(payload.get("url", "unknown"))
        previous_content = payload.get("previous_content")
        current_content = str(payload.get("current_content", ""))

        changes: list[str] = []
        risk_flags: list[str] = []

        if previous_content is None:
            changes.append("initial_capture")
        elif str(previous_content) == current_content:
            changes.append("no_textual_change")
        else:
            changes.append("content_changed")
            delta = len(current_content) - len(str(previous_content))
            if abs(delta) > 500:
                risk_flags.append("large_content_delta")
            lowered = current_content.lower()
            if "password" in lowered or "credential" in lowered:
                risk_flags.append("sensitive_keywords_detected")

        summary = (
            f"Analyzed monitor content for {url}. "
            f"Detected: {', '.join(changes)}. "
            f"Risk flags: {', '.join(risk_flags) if risk_flags else 'none'}."
        )
        return {
            "summary": summary,
            "detected_changes": changes,
            "risk_flags": risk_flags,
        }
