"""Tests for MedLens agent pipeline.

Tests agent interfaces, data structures, and the orchestrator pipeline.
Model-dependent tests are marked with @pytest.mark.gpu and skipped
when no CUDA device is available.
"""

from __future__ import annotations

import pytest

from medlens.agents.parsing import extract_list, extract_section, parse_confidence, parse_urgency
from medlens.agents.visual import VisualAnalysisAgent, VisualFindings
from medlens.agents.reasoning import (
    ClinicalAssessment,
    ClinicalReasoningAgent,
    PatientContext,
)
from medlens.agents.report import (
    PatientReport,
    PatientReportAgent,
    compute_flesch_kincaid_grade,
)


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


class TestSharedParsing:
    """Test shared parsing utilities."""

    def test_extract_section_basic(self):
        text = "DESCRIPTION: Some finding here\nMORPHOLOGY: papule"
        result = extract_section(text, "DESCRIPTION")
        assert result == "Some finding here"

    def test_extract_section_case_insensitive(self):
        text = "description: Some finding here\nMORPHOLOGY: papule"
        result = extract_section(text, "DESCRIPTION")
        assert result == "Some finding here"

    def test_extract_list_strips_bullets(self):
        text = "MORPHOLOGY: -papule, -raised, \u2022dome-shaped\nSEVERITY: mild"
        result = extract_list(text, "MORPHOLOGY")
        assert "papule" in result
        assert "raised" in result
        assert "dome-shaped" in result

    def test_extract_list_numbered(self):
        text = (
            "DIFFERENTIAL DIAGNOSIS: \n"
            "1) melanoma\n"
            "2) dysplastic nevus\n"
            "3) seborrheic keratosis\n"
            "URGENCY: routine"
        )
        result = extract_list(text, "DIFFERENTIAL DIAGNOSIS")
        assert len(result) >= 3
        assert any("melanoma" in item for item in result)

    def test_parse_confidence_values(self):
        assert parse_confidence("high") == 0.9
        assert parse_confidence("moderate") == 0.7
        assert parse_confidence("medium") == 0.7
        assert parse_confidence("low") == 0.4
        assert parse_confidence("0.85") == 0.85
        assert parse_confidence("85%") == 0.85
        assert parse_confidence("") == 0.0
        assert parse_confidence("unknown") == 0.0

    def test_parse_urgency_values(self):
        assert parse_urgency("routine") == "routine"
        assert parse_urgency("Urgent") == "urgent"
        assert parse_urgency("EMERGENT") == "emergent"
        assert parse_urgency("Urgent - needs attention") == "urgent"
        assert parse_urgency("") == "routine"


class TestVisualAnalysisAgentParsing:
    """Test VisualAnalysisAgent output parsing (no model needed)."""

    SAMPLE_OUTPUT = (
        "DESCRIPTION: Erythematous papule with irregular borders on the dorsal "
        "surface of the left forearm. The lesion appears raised with surrounding "
        "mild erythema.\n"
        "MORPHOLOGY: papule, raised, irregular shape, dome-shaped\n"
        "ANATOMICAL LOCATION: left forearm, dorsal surface\n"
        "SEVERITY: moderate\n"
        "COLOR DESCRIPTORS: erythematous, pink, brown center\n"
        "SIZE ESTIMATE: approximately 5mm in diameter\n"
        "BORDER CHARACTERISTICS: irregular, poorly defined margins with "
        "asymmetric outline\n"
        "ADDITIONAL OBSERVATIONS: no ulceration, no satellite lesions, mild "
        "surrounding erythema\n"
        "CONFIDENCE: high"
    )

    def test_parse_structured_output(self):
        findings = VisualAnalysisAgent._parse_output(self.SAMPLE_OUTPUT)
        assert "Erythematous papule" in findings.description
        assert "papule" in findings.morphology
        assert "left forearm" in findings.anatomical_location
        assert findings.severity == "moderate"
        assert "erythematous" in findings.color_descriptors
        assert "5mm" in findings.size_estimate
        assert "irregular" in findings.border_characteristics
        assert len(findings.additional_observations) >= 2
        assert findings.confidence == 0.9  # "high" -> 0.9
        assert findings.raw_output == self.SAMPLE_OUTPUT

    def test_parse_empty_output(self):
        findings = VisualAnalysisAgent._parse_output("")
        assert findings.description == ""
        assert findings.morphology == []
        assert findings.confidence == 0.0

    def test_parse_unstructured_fallback(self):
        raw = "This is an unstructured description without any headers."
        findings = VisualAnalysisAgent._parse_output(raw)
        # Fallback: entire output becomes the description
        assert findings.description == raw

    def test_build_prompt_without_context(self):
        agent = VisualAnalysisAgent.__new__(VisualAnalysisAgent)
        prompt = agent._build_prompt("")
        assert "Clinical context" not in prompt
        assert "DESCRIPTION:" in prompt

    def test_build_prompt_with_context(self):
        agent = VisualAnalysisAgent.__new__(VisualAnalysisAgent)
        prompt = agent._build_prompt("left forearm lesion")
        assert "Clinical context: left forearm lesion" in prompt


class TestClinicalReasoningAgentParsing:
    """Test ClinicalReasoningAgent output parsing (no model needed)."""

    SAMPLE_OUTPUT = (
        "SUBJECTIVE: Patient is a 45-year-old male presenting with a growing "
        "mole on the left forearm. Reports the lesion has changed in size over "
        "the past 3 months. No pain or bleeding.\n"
        "OBJECTIVE: Visual analysis reveals an erythematous papule with irregular "
        "borders on the dorsal surface of the left forearm, approximately 5mm in "
        "diameter. Moderate severity. No ulceration noted.\n"
        "ASSESSMENT: Atypical nevus with features concerning for possible "
        "dysplastic change. The irregular borders and changing size warrant further "
        "evaluation to rule out melanoma.\n"
        "PLAN: Refer to dermatology for dermoscopic evaluation and possible "
        "excisional biopsy. Educate patient on ABCDE criteria for melanoma "
        "self-monitoring. Follow-up in 2 weeks.\n"
        "DIFFERENTIAL DIAGNOSIS: dysplastic nevus, melanoma, seborrheic keratosis, "
        "basal cell carcinoma\n"
        "RECOMMENDED WORKUP: dermoscopy, excisional biopsy with histopathology, "
        "full skin exam\n"
        "URGENCY: urgent\n"
        "CONFIDENCE: high"
    )

    def test_parse_structured_output(self):
        result = ClinicalReasoningAgent._parse_output(self.SAMPLE_OUTPUT)
        assert "45-year-old male" in result.subjective
        assert "erythematous papule" in result.objective
        assert "Atypical nevus" in result.assessment
        assert "dermatology" in result.plan
        assert len(result.differential_diagnosis) >= 3
        assert "dysplastic nevus" in result.differential_diagnosis
        assert len(result.recommended_workup) >= 2
        assert result.urgency == "urgent"
        assert result.confidence == 0.9  # "high" -> 0.9
        assert result.raw_output == self.SAMPLE_OUTPUT

    def test_parse_empty_output(self):
        result = ClinicalReasoningAgent._parse_output("")
        assert result.subjective == ""
        assert result.objective == ""
        assert result.assessment == ""
        assert result.plan == ""
        assert result.differential_diagnosis == []
        assert result.urgency == "routine"  # default
        assert result.confidence == 0.0

    def test_parse_unstructured_fallback(self):
        raw = "This patient likely has a benign lesion that should be monitored."
        result = ClinicalReasoningAgent._parse_output(raw)
        # Fallback: entire output becomes the assessment
        assert result.assessment == raw

    def test_soap_note_property(self):
        result = ClinicalReasoningAgent._parse_output(self.SAMPLE_OUTPUT)
        soap = result.soap_note
        assert "SUBJECTIVE:" in soap
        assert "OBJECTIVE:" in soap
        assert "ASSESSMENT:" in soap
        assert "PLAN:" in soap
        assert "45-year-old male" in soap

    def test_build_prompt_with_full_context(self):
        agent = ClinicalReasoningAgent.__new__(ClinicalReasoningAgent)
        findings = VisualFindings(
            description="Erythematous papule",
            morphology=["papule", "raised"],
            anatomical_location="left forearm",
            severity="moderate",
            confidence=0.9,
        )
        context = PatientContext(
            age="45",
            sex="male",
            chief_complaint="growing mole",
        )
        prompt = agent._build_prompt(findings, context)
        assert "Erythematous papule" in prompt
        assert "left forearm" in prompt
        assert "Age: 45" in prompt
        assert "Chief complaint: growing mole" in prompt
        assert "SUBJECTIVE:" in prompt
        assert "DIFFERENTIAL DIAGNOSIS:" in prompt

    def test_build_prompt_empty_context(self):
        agent = ClinicalReasoningAgent.__new__(ClinicalReasoningAgent)
        findings = VisualFindings()
        context = PatientContext()
        prompt = agent._build_prompt(findings, context)
        assert "No visual findings available" in prompt
        assert "No patient context provided" in prompt

    def test_format_findings(self):
        findings = VisualFindings(
            description="A lesion",
            morphology=["papule"],
            severity="mild",
        )
        text = ClinicalReasoningAgent._format_findings(findings)
        assert "Description: A lesion" in text
        assert "Morphology: papule" in text
        assert "Severity: mild" in text

    def test_format_context(self):
        context = PatientContext(
            age="30",
            sex="female",
            medications="ibuprofen",
        )
        text = ClinicalReasoningAgent._format_context(context)
        assert "Age: 30" in text
        assert "Sex: female" in text
        assert "Medications: ibuprofen" in text


class TestPatientReportAgentParsing:
    """Test PatientReportAgent output parsing (no model needed)."""

    SAMPLE_OUTPUT = (
        "SUMMARY: We looked at an image of a spot on your left arm. It has some "
        "features that your doctor should check more closely.\n"
        "WHAT WE FOUND: There is a small raised spot on your left forearm. It is "
        "about 5mm wide (about the size of a pencil eraser). The spot has uneven "
        "edges and is pinkish-brown in color.\n"
        "WHAT IT MIGHT MEAN: This kind of spot could be a mole that is changing. "
        "Most changing moles are not dangerous, but it is important to have a "
        "doctor look at it to be sure.\n"
        "NEXT STEPS: You should see a skin doctor (dermatologist) soon. They may "
        "want to look at the spot with a special magnifying tool and possibly "
        "take a small sample to test.\n"
        "QUESTIONS TO ASK YOUR DOCTOR: What type of spot is this?, Do I need a "
        "biopsy?, How quickly should I be seen?, What signs should I watch for?"
    )

    def test_parse_structured_output(self):
        result = PatientReportAgent._parse_output(self.SAMPLE_OUTPUT)
        assert "spot on your left arm" in result.summary
        assert "small raised spot" in result.what_we_found
        assert "mole that is changing" in result.what_it_might_mean
        assert "skin doctor" in result.next_steps
        assert len(result.questions_to_ask) >= 3
        assert any("biopsy" in q for q in result.questions_to_ask)
        assert result.raw_output == self.SAMPLE_OUTPUT
        assert result.flesch_kincaid_grade > 0.0

    def test_parse_empty_output(self):
        result = PatientReportAgent._parse_output("")
        assert result.summary == ""
        assert result.what_we_found == ""
        assert result.what_it_might_mean == ""
        assert result.next_steps == ""
        assert result.questions_to_ask == []
        assert result.flesch_kincaid_grade == 0.0

    def test_parse_unstructured_fallback(self):
        raw = "Your doctor found a spot on your arm that needs a closer look."
        result = PatientReportAgent._parse_output(raw)
        # Fallback: entire output becomes the summary
        assert result.summary == raw
        assert result.flesch_kincaid_grade > 0.0

    def test_flesch_kincaid_computed(self):
        result = PatientReportAgent._parse_output(self.SAMPLE_OUTPUT)
        # Patient-friendly text should be at a reasonable reading level
        assert result.flesch_kincaid_grade > 0.0
        assert result.flesch_kincaid_grade < 20.0

    def test_build_prompt_with_full_assessment(self):
        agent = PatientReportAgent.__new__(PatientReportAgent)
        assessment = ClinicalAssessment(
            subjective="Patient reports a growing mole.",
            objective="5mm erythematous papule on left forearm.",
            assessment="Atypical nevus, rule out melanoma.",
            plan="Refer to dermatology for biopsy.",
            differential_diagnosis=["dysplastic nevus", "melanoma"],
            recommended_workup=["dermoscopy", "biopsy"],
            urgency="urgent",
        )
        prompt = agent._build_prompt(assessment)
        assert "growing mole" in prompt
        assert "5mm erythematous papule" in prompt
        assert "Atypical nevus" in prompt
        assert "dermatology" in prompt
        assert "dysplastic nevus" in prompt
        assert "SUMMARY:" in prompt

    def test_build_prompt_empty_assessment(self):
        agent = PatientReportAgent.__new__(PatientReportAgent)
        assessment = ClinicalAssessment()
        prompt = agent._build_prompt(assessment)
        assert "No clinical assessment available" in prompt

    def test_format_assessment(self):
        assessment = ClinicalAssessment(
            subjective="Growing mole.",
            objective="5mm papule.",
            assessment="Atypical nevus.",
            plan="Refer to dermatology.",
            urgency="urgent",
        )
        text = PatientReportAgent._format_assessment(assessment)
        assert "Subjective: Growing mole." in text
        assert "Objective: 5mm papule." in text
        assert "Assessment: Atypical nevus." in text
        assert "Plan: Refer to dermatology." in text
        assert "Urgency: urgent" in text

    def test_format_assessment_empty(self):
        assessment = ClinicalAssessment()
        text = PatientReportAgent._format_assessment(assessment)
        assert text == "No clinical assessment available."

    def test_extract_list_comma_separated(self):
        text = (
            "QUESTIONS TO ASK YOUR DOCTOR: What is this spot?, "
            "Do I need treatment?, When should I follow up?\n"
        )
        result = extract_list(text, "QUESTIONS TO ASK YOUR DOCTOR")
        assert len(result) == 3
        assert any("treatment" in q for q in result)

    def test_extract_list_bulleted(self):
        text = (
            "QUESTIONS TO ASK YOUR DOCTOR:\n"
            "- What is this spot?\n"
            "- Do I need a biopsy?\n"
            "- How soon should I be seen?\n"
        )
        result = extract_list(text, "QUESTIONS TO ASK YOUR DOCTOR")
        assert len(result) >= 3
        assert any("biopsy" in q for q in result)

    def test_report_has_disclaimer(self):
        result = PatientReportAgent._parse_output(self.SAMPLE_OUTPUT)
        assert "NOT a medical diagnosis" in result.disclaimer
