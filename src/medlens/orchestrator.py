"""Orchestrator — Agentic workflow coordinator.

Chains the 3 MedLens agents (Visual Analysis → Clinical Reasoning →
Patient Report) with observable intermediate outputs. Manages the
pipeline flow, timing, and error handling.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image

from medlens.agents.reasoning import ClinicalAssessment, PatientContext
from medlens.agents.report import PatientReport
from medlens.agents.visual import VisualFindings


@dataclass
class PipelineResult:
    """Complete result from the 3-agent pipeline."""

    visual_findings: VisualFindings | None = None
    clinical_assessment: ClinicalAssessment | None = None
    patient_report: PatientReport | None = None
    timings: dict[str, float] = field(default_factory=dict)
    total_time: float = 0.0
    success: bool = False
    error: str = ""

    @property
    def soap_note(self) -> str:
        if self.clinical_assessment:
            return self.clinical_assessment.soap_note
        return ""


class MedLensOrchestrator:
    """Coordinates the 3-agent pipeline.

    Usage:
        model = MedGemmaModel(config)
        model.load()
        orchestrator = MedLensOrchestrator(model)
        result = orchestrator.run(image, patient_context)
    """

    def __init__(self, model) -> None:
        from medlens.agents.reasoning import ClinicalReasoningAgent
        from medlens.agents.report import PatientReportAgent
        from medlens.agents.visual import VisualAnalysisAgent

        self.visual_agent = VisualAnalysisAgent(model)
        self.reasoning_agent = ClinicalReasoningAgent(model)
        self.report_agent = PatientReportAgent(model)

    def run(
        self,
        image: Image.Image,
        patient_context: PatientContext,
        clinical_context: str = "",
    ) -> PipelineResult:
        """Run the full 3-agent pipeline.

        Args:
            image: Clinical image to analyze.
            patient_context: Patient demographics and history.
            clinical_context: Optional brief context for image analysis.

        Returns:
            PipelineResult with all intermediate and final outputs.
        """
        result = PipelineResult()
        pipeline_start = time.time()

        try:
            # Agent 1: Visual Analysis
            t0 = time.time()
            result.visual_findings = self.visual_agent.run(image, clinical_context)
            result.timings["visual_analysis"] = time.time() - t0

            # Agent 2: Clinical Reasoning
            t0 = time.time()
            result.clinical_assessment = self.reasoning_agent.run(
                result.visual_findings, patient_context
            )
            result.timings["clinical_reasoning"] = time.time() - t0

            # Agent 3: Patient Report
            t0 = time.time()
            result.patient_report = self.report_agent.run(result.clinical_assessment)
            result.timings["patient_report"] = time.time() - t0

            result.success = True

        except Exception as e:
            result.error = str(e)
            result.success = False

        result.total_time = time.time() - pipeline_start
        return result
