"""Agent 1: Visual Analysis Agent.

Takes a clinical image and runs MedGemma multimodal inference to produce
structured findings including morphology, anatomical location, severity,
and visual descriptors.

Input: PIL Image + optional clinical context
Output: VisualFindings dataclass with structured observations
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from medlens.agents.parsing import extract_list, extract_section, parse_confidence

if TYPE_CHECKING:
    from PIL import Image

    from medlens.model import MedGemmaModel

logger = logging.getLogger(__name__)


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

    USER_PROMPT_TEMPLATE = (
        "Analyze this clinical image and provide your findings in the following "
        "structured format. Use exactly these section headers:\n\n"
        "DESCRIPTION: <one paragraph overall description>\n"
        "MORPHOLOGY: <comma-separated list of morphological features>\n"
        "ANATOMICAL LOCATION: <body location>\n"
        "SEVERITY: <mild, moderate, or severe>\n"
        "COLOR DESCRIPTORS: <comma-separated list of colors observed>\n"
        "SIZE ESTIMATE: <estimated size or extent>\n"
        "BORDER CHARACTERISTICS: <description of borders/margins>\n"
        "ADDITIONAL OBSERVATIONS: <comma-separated list of other notable findings>\n"
        "CONFIDENCE: <high, moderate, or low>\n"
        "{context}"
    )

    # Agent-specific generation config (from model_config.yaml agents.visual)
    MAX_NEW_TOKENS = 768
    TEMPERATURE = 0.2

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
        prompt = self._build_prompt(clinical_context)

        logger.info("Running visual analysis agent")
        raw_output = self.model.generate_multimodal(
            image=image,
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            max_new_tokens=self.MAX_NEW_TOKENS,
            temperature=self.TEMPERATURE,
        )
        logger.debug("Visual agent raw output: %s", raw_output)

        return self._parse_output(raw_output)

    def _build_prompt(self, clinical_context: str) -> str:
        """Build the user prompt, optionally including clinical context."""
        context_line = ""
        if clinical_context.strip():
            context_line = f"\nClinical context: {clinical_context.strip()}"
        return self.USER_PROMPT_TEMPLATE.format(context=context_line)

    @staticmethod
    def _parse_output(raw_output: str) -> VisualFindings:
        """Parse LLM output into structured VisualFindings.

        Uses section-header regex matching with fallback to treating the
        entire output as a description if structured parsing fails.
        """
        findings = VisualFindings(raw_output=raw_output)

        findings.description = extract_section(raw_output, "DESCRIPTION")
        findings.morphology = extract_list(raw_output, "MORPHOLOGY")
        findings.anatomical_location = extract_section(
            raw_output, "ANATOMICAL LOCATION"
        )
        findings.severity = extract_section(raw_output, "SEVERITY").lower()
        findings.color_descriptors = extract_list(raw_output, "COLOR DESCRIPTORS")
        findings.size_estimate = extract_section(raw_output, "SIZE ESTIMATE")
        findings.border_characteristics = extract_section(
            raw_output, "BORDER CHARACTERISTICS"
        )
        findings.additional_observations = extract_list(
            raw_output, "ADDITIONAL OBSERVATIONS"
        )
        findings.confidence = parse_confidence(
            extract_section(raw_output, "CONFIDENCE")
        )

        # Fallback: if no structured sections were parsed, use full output as description
        if not findings.description and raw_output.strip():
            findings.description = raw_output.strip()

        return findings
