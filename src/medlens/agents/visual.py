"""Agent 1: Visual Analysis Agent.

Takes a clinical image and runs MedGemma multimodal inference to produce
structured findings including morphology, anatomical location, severity,
and visual descriptors.

Input: PIL Image + optional clinical context
Output: VisualFindings dataclass with structured observations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image

    from medlens.model import MedGemmaModel


@dataclass
class VisualFindings:
    """Structured output from visual analysis."""

    description: str = ""
    morphology: list[str] = field(default_factory=list)
    anatomical_location: str = ""
    severity: str = ""
    color_descriptors: list[str] = field(default_factory=list)
    size_estimate: str = ""
    border_characteristics: str = ""
    additional_observations: list[str] = field(default_factory=list)
    confidence: float = 0.0
    raw_output: str = ""


class VisualAnalysisAgent:
    """Analyzes clinical images using MedGemma multimodal capabilities.

    This is the first agent in the pipeline. It receives a clinical image
    and produces structured visual findings that feed into the Clinical
    Reasoning Agent.
    """

    SYSTEM_PROMPT = (
        "You are a medical image analysis assistant. Analyze the provided clinical "
        "image and describe your findings in a structured format. Include: "
        "1) Overall description, 2) Morphological features, 3) Anatomical location, "
        "4) Severity assessment, 5) Color descriptors, 6) Size estimate, "
        "7) Border characteristics, 8) Any additional observations. "
        "Be thorough but factual. Do not diagnose — only describe what you observe."
    )

    def __init__(self, model: MedGemmaModel) -> None:
        self.model = model

    def run(self, image: Image.Image, clinical_context: str = "") -> VisualFindings:
        """Analyze a clinical image and return structured findings.

        Args:
            image: PIL Image of the clinical finding.
            clinical_context: Optional brief context (e.g., "left forearm lesion").

        Returns:
            VisualFindings with structured observations.
        """
        raise NotImplementedError("Visual analysis agent not yet implemented")
