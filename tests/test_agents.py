"""Tests for MedLens agent pipeline.

Tests agent interfaces, data structures, and the orchestrator pipeline.
Model-dependent tests are marked with @pytest.mark.gpu and skipped
when no CUDA device is available.
"""

from __future__ import annotations

import pytest

from medlens.agents.visual import VisualFindings
from medlens.agents.reasoning import ClinicalAssessment, PatientContext
from medlens.agents.report import PatientReport, compute_flesch_kincaid_grade


class TestDataStructures:
    """Test agent input/output data structures."""

    def test_visual_findings_defaults(self):
        findings = VisualFindings()
        assert findings.description == ""
        assert findings.morphology == []
        assert findings.confidence == 0.0

    def test_visual_findings_populated(self):
        findings = VisualFindings(
            description="Erythematous papule",
            morphology=["papule", "raised"],
            anatomical_location="left forearm",
            severity="mild",
            confidence=0.85,
        )
        assert findings.description == "Erythematous papule"
        assert len(findings.morphology) == 2
        assert findings.confidence == 0.85

    def test_patient_context_defaults(self):
        ctx = PatientContext()
        assert ctx.age == ""
        assert ctx.chief_complaint == ""

    def test_clinical_assessment_soap_note(self):
        assessment = ClinicalAssessment(
            subjective="Patient reports a growing mole.",
            objective="3mm dark papule on left forearm.",
            assessment="Atypical nevus, rule out melanoma.",
            plan="Refer to dermatology for biopsy.",
        )
        soap = assessment.soap_note
        assert "SUBJECTIVE:" in soap
        assert "OBJECTIVE:" in soap
        assert "ASSESSMENT:" in soap
        assert "PLAN:" in soap
        assert "growing mole" in soap

    def test_patient_report_has_disclaimer(self):
        report = PatientReport()
        assert "NOT a medical diagnosis" in report.disclaimer

    def test_patient_report_questions_default(self):
        report = PatientReport()
        assert report.questions_to_ask == []


class TestFleschKincaid:
    """Test Flesch-Kincaid grade level computation."""

    def test_simple_text(self):
        text = "The cat sat on the mat. It was a good cat."
        grade = compute_flesch_kincaid_grade(text)
        assert grade < 5.0  # Very simple text

    def test_complex_text(self):
        text = (
            "The dermatological examination revealed an erythematous papule "
            "with irregular borders and heterogeneous pigmentation consistent "
            "with a potentially malignant neoplastic transformation."
        )
        grade = compute_flesch_kincaid_grade(text)
        assert grade > 10.0  # Complex medical text

    def test_empty_text(self):
        grade = compute_flesch_kincaid_grade("")
        assert grade >= 0.0
