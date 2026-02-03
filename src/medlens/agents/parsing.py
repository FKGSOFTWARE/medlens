"""Shared parsing utilities for agent output extraction.

All three agents (visual, reasoning, report) parse structured LLM output
using section-header regex matching. This module provides the common
extraction functions to avoid duplication.
"""

from __future__ import annotations

import re


def extract_section(text: str, header: str) -> str:
    """Extract the value after a section header.

    Matches 'HEADER:' followed by content, ending at the next header or end of text.
    """
    pattern = rf"(?i){re.escape(header)}\s*:\s*(.+?)(?=\n[A-Z][\w\s]*:|$)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def extract_list(text: str, header: str) -> list[str]:
    """Extract a comma-separated or numbered/bulleted list from a section."""
    pattern = rf"(?i){re.escape(header)}\s*:\s*(.+?)(?=\n[A-Z][\w\s]*:|$)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        raw = match.group(1).strip()
        items = re.split(r",|\n\s*\d+[.)]\s*|\n\s*[-•]\s*", raw)
        return [item.strip().strip("-•).").strip() for item in items if item.strip()]
    return []


def parse_confidence(confidence_str: str) -> float:
    """Convert confidence string to a float score."""
    confidence_str = confidence_str.lower().strip()
    mapping = {
        "high": 0.9,
        "moderate": 0.7,
        "medium": 0.7,
        "low": 0.4,
    }
    for key, value in mapping.items():
        if key in confidence_str:
            return value
    numeric = re.search(r"(\d+\.?\d*)", confidence_str)
    if numeric:
        val = float(numeric.group(1))
        return val / 100.0 if val > 1.0 else val
    return 0.0


def parse_urgency(urgency_str: str) -> str:
    """Normalize urgency string to one of: routine, urgent, emergent."""
    urgency_str = urgency_str.lower().strip()
    for level in ("emergent", "urgent", "routine"):
        if level in urgency_str:
            return level
    return urgency_str if urgency_str else "routine"
