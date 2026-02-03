"""Agent 2: Clinical Reasoning Agent.

Takes visual findings from Agent 1 plus patient context (demographics,
history, symptoms) and produces a clinical assessment including differential
diagnosis, recommended workup, urgency assessment, and a SOAP-format note.

Input: VisualFindings + PatientContext
Output: ClinicalAssessment dataclass with SOAP note and differentials
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from medlens.agents.parsing import (
    extract_list,
    extract_section,
    parse_confidence,
    parse_urgency,
)

if TYPE_CHECKING:
    from medlens.agents.visual import VisualFindings
    from medlens.model import MedGemmaModel

logger = logging.getLogger(__name__)


@dataclass
class PatientContext:
    """Patient demographic and clinical context."""

    age: str = ""
    sex: str = ""
    chief_complaint: str = ""
    history_of_present_illness: str = ""
    past_medical_history: str = ""
    medications: str = ""
    allergies: str = ""
    additional_notes: str = ""


@dataclass
class ClinicalAssessment:
    """Structured output from clinical reasoning."""

    # SOAP Note
    subjective: str = ""
    objective: str = ""
    assessment: str = ""
    plan: str = ""

    # Differentials
    differential_diagnosis: list[str] = field(default_factory=list)
    recommended_workup: list[str] = field(default_factory=list)
    urgency: str = ""  # routine, urgent, emergent
    confidence: float = 0.0
    raw_output: str = ""

    @property
    def soap_note(self) -> str:
        """Format as a standard SOAP note."""
        return (
            f"SUBJECTIVE:\n{self.subjective}\n\n"
            f"OBJECTIVE:\n{self.objective}\n\n"
            f"ASSESSMENT:\n{self.assessment}\n\n"
            f"PLAN:\n{self.plan}"
        )


class ClinicalReasoningAgent:
    """Integrates visual findings with patient context for clinical reasoning.

    This is the second agent in the pipeline. It receives structured visual
    findings from Agent 1 and patient context, then produces a clinical
    assessment including differential diagnosis and SOAP note.
    """

    SYSTEM_PROMPT = (
        "You are a clinical reasoning assistant. Given visual findings from a "
        "clinical image analysis and patient context, provide a structured clinical "
        "assessment. Include: 1) SOAP note (Subjective, Objective, Assessment, Plan), "
        "2) Differential diagnosis (ranked by likelihood), 3) Recommended workup, "
        "4) Urgency assessment (routine/urgent/emergent). "
        "This is for clinical decision support only — not a definitive diagnosis."
    )

    USER_PROMPT_TEMPLATE = (
        "Based on the following visual findings and patient context, provide a "
        "structured clinical assessment. Use exactly these section headers:\n\n"
        "SUBJECTIVE: <patient-reported symptoms and history>\n"
        "OBJECTIVE: <visual findings and clinical observations>\n"
        "ASSESSMENT: <clinical interpretation and primary impression>\n"
        "PLAN: <recommended next steps and management>\n"
        "DIFFERENTIAL DIAGNOSIS: <comma-separated list ranked by likelihood>\n"
        "RECOMMENDED WORKUP: <comma-separated list of tests/procedures>\n"
        "URGENCY: <routine, urgent, or emergent>\n"
        "CONFIDENCE: <high, moderate, or low>\n\n"
        "--- VISUAL FINDINGS ---\n{findings}\n\n"
        "--- PATIENT CONTEXT ---\n{context}"
    )

    # Agent-specific generation config (from model_config.yaml agents.reasoning)
    MAX_NEW_TOKENS = 1024
    TEMPERATURE = 0.3

    def __init__(self, model: MedGemmaModel) -> None:
        self.model = model

    def run(
        self, findings: VisualFindings, context: PatientContext
    ) -> ClinicalAssessment:
        """Produce clinical assessment from visual findings and patient context.

        Args:
            findings: Structured visual findings from Agent 1.
            context: Patient demographic and clinical context.

        Returns:
            ClinicalAssessment with SOAP note and differentials.
        """
        prompt = self._build_prompt(findings, context)

        logger.info("Running clinical reasoning agent")
        raw_output = self.model.generate_text(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            max_new_tokens=self.MAX_NEW_TOKENS,
            temperature=self.TEMPERATURE,
        )
        logger.debug("Reasoning agent raw output: %s", raw_output)

        return self._parse_output(raw_output)

    def _build_prompt(
        self, findings: VisualFindings, context: PatientContext
    ) -> str:
        """Build the user prompt from visual findings and patient context."""
        findings_text = self._format_findings(findings)
        context_text = self._format_context(context)
        return self.USER_PROMPT_TEMPLATE.format(
            findings=findings_text, context=context_text
        )

    @staticmethod
    def _format_findings(findings: VisualFindings) -> str:
        """Format VisualFindings into a readable text block."""
        parts: list[str] = []
        if findings.description:
            parts.append(f"Description: {findings.description}")
        if findings.morphology:
            parts.append(f"Morphology: {', '.join(findings.morphology)}")
        if findings.anatomical_location:
            parts.append(f"Anatomical location: {findings.anatomical_location}")
        if findings.severity:
            parts.append(f"Severity: {findings.severity}")
        if findings.color_descriptors:
            parts.append(f"Color: {', '.join(findings.color_descriptors)}")
        if findings.size_estimate:
            parts.append(f"Size: {findings.size_estimate}")
        if findings.border_characteristics:
            parts.append(f"Borders: {findings.border_characteristics}")
        if findings.additional_observations:
            parts.append(
                f"Additional: {', '.join(findings.additional_observations)}"
            )
        if findings.confidence > 0:
            parts.append(f"Visual confidence: {findings.confidence:.1f}")
        return "\n".join(parts) if parts else "No visual findings available."

    @staticmethod
    def _format_context(context: PatientContext) -> str:
        """Format PatientContext into a readable text block."""
        parts: list[str] = []
        if context.age:
            parts.append(f"Age: {context.age}")
        if context.sex:
            parts.append(f"Sex: {context.sex}")
        if context.chief_complaint:
            parts.append(f"Chief complaint: {context.chief_complaint}")
        if context.history_of_present_illness:
            parts.append(f"HPI: {context.history_of_present_illness}")
        if context.past_medical_history:
            parts.append(f"PMH: {context.past_medical_history}")
        if context.medications:
            parts.append(f"Medications: {context.medications}")
        if context.allergies:
            parts.append(f"Allergies: {context.allergies}")
        if context.additional_notes:
            parts.append(f"Notes: {context.additional_notes}")
        return "\n".join(parts) if parts else "No patient context provided."

    @staticmethod
    def _parse_output(raw_output: str) -> ClinicalAssessment:
        """Parse LLM output into structured ClinicalAssessment.

        Uses section-header regex matching with fallback to treating the
        entire output as the assessment field if structured parsing fails.
        """
        result = ClinicalAssessment(raw_output=raw_output)

        result.subjective = extract_section(raw_output, "SUBJECTIVE")
        result.objective = extract_section(raw_output, "OBJECTIVE")
        result.assessment = extract_section(raw_output, "ASSESSMENT")
        result.plan = extract_section(raw_output, "PLAN")
        result.differential_diagnosis = extract_list(
            raw_output, "DIFFERENTIAL DIAGNOSIS"
        )
        result.recommended_workup = extract_list(
            raw_output, "RECOMMENDED WORKUP"
        )
        result.urgency = parse_urgency(
            extract_section(raw_output, "URGENCY")
        )
        result.confidence = parse_confidence(
            extract_section(raw_output, "CONFIDENCE")
        )

        # Fallback: if no SOAP sections were parsed, use full output as assessment
        if not any([result.subjective, result.objective,
                     result.assessment, result.plan]) and raw_output.strip():
            result.assessment = raw_output.strip()

        return result
