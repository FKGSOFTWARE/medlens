"""Agent 2: Clinical Reasoning Agent.

Takes visual findings from Agent 1 plus patient context (demographics,
history, symptoms) and produces a clinical assessment including differential
diagnosis, recommended workup, urgency assessment, and a SOAP-format note.

Input: VisualFindings + PatientContext
Output: ClinicalAssessment dataclass with SOAP note and differentials
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from medlens.agents.visual import VisualFindings
    from medlens.model import MedGemmaModel


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
        raise NotImplementedError("Clinical reasoning agent not yet implemented")
