"""MedLens Streamlit Application.

Provides a web interface for uploading clinical images, entering patient
context, and viewing the 3-agent pipeline results including intermediate
outputs at each stage.
"""

from __future__ import annotations

import logging

import streamlit as st
from PIL import Image

from medlens.agents.reasoning import ClinicalAssessment, PatientContext
from medlens.agents.report import PatientReport
from medlens.agents.visual import VisualFindings
from medlens.model import MedGemmaModel, ModelConfig
from medlens.orchestrator import MedLensOrchestrator, PipelineResult

logger = logging.getLogger(__name__)

# --- Page configuration ---

st.set_page_config(
    page_title="MedLens — Clinical Image Analysis",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Constants ---

DISCLAIMER_TEXT = (
    "**Disclaimer:** MedLens is an AI-powered clinical decision support tool. "
    "It is **NOT** a substitute for professional medical advice, diagnosis, or "
    "treatment. All outputs are for informational and educational purposes only. "
    "Always consult a qualified healthcare provider."
)

CONFIG_PATH = "configs/model_config.yaml"


# --- Model loading (cached) ---


@st.cache_resource(show_spinner="Loading MedGemma model — this may take a moment...")
def load_model() -> MedGemmaModel:
    """Load the MedGemma model once and cache across sessions."""
    try:
        model = MedGemmaModel.from_yaml(CONFIG_PATH)
    except FileNotFoundError:
        model = MedGemmaModel(ModelConfig())
    model.load()
    return model


# --- Helper functions ---


def render_disclaimer() -> None:
    """Display the clinical disclaimer banner."""
    st.warning(DISCLAIMER_TEXT)


def render_sidebar_metrics(result: PipelineResult) -> None:
    """Display pipeline timing metrics in the sidebar."""
    st.sidebar.markdown("## Pipeline Metrics")

    if result.timings:
        for stage, duration in result.timings.items():
            label = stage.replace("_", " ").title()
            st.sidebar.metric(label, f"{duration:.1f}s")

    st.sidebar.metric("Total Time", f"{result.total_time:.1f}s")
    st.sidebar.markdown("---")

    target = 30.0
    if result.total_time <= target:
        st.sidebar.success(f"Within {target:.0f}s target")
    else:
        st.sidebar.warning(f"Exceeded {target:.0f}s target")


def render_visual_findings(findings: VisualFindings) -> None:
    """Render visual analysis findings in an expandable section."""
    with st.expander("Agent 1: Visual Analysis", expanded=False):
        if findings.description:
            st.markdown(f"**Description:** {findings.description}")
        if findings.morphology:
            st.markdown(f"**Morphology:** {', '.join(findings.morphology)}")
        if findings.anatomical_location:
            st.markdown(f"**Anatomical Location:** {findings.anatomical_location}")
        if findings.severity:
            st.markdown(f"**Severity:** {findings.severity}")
        if findings.color_descriptors:
            st.markdown(f"**Color Descriptors:** {', '.join(findings.color_descriptors)}")
        if findings.size_estimate:
            st.markdown(f"**Size Estimate:** {findings.size_estimate}")
        if findings.border_characteristics:
            st.markdown(f"**Border Characteristics:** {findings.border_characteristics}")
        if findings.additional_observations:
            st.markdown(
                f"**Additional Observations:** {', '.join(findings.additional_observations)}"
            )
        if findings.confidence > 0:
            st.markdown(f"**Confidence:** {findings.confidence:.0%}")

        with st.expander("Raw Output"):
            st.code(findings.raw_output, language=None)


def render_clinical_assessment(assessment: ClinicalAssessment) -> None:
    """Render clinical assessment (SOAP note) in an expandable section."""
    with st.expander("Agent 2: Clinical Reasoning", expanded=False):
        st.markdown("### SOAP Note")
        soap_tab, details_tab = st.tabs(["SOAP Note", "Details"])

        with soap_tab:
            st.markdown(f"**Subjective:**\n{assessment.subjective}")
            st.markdown(f"**Objective:**\n{assessment.objective}")
            st.markdown(f"**Assessment:**\n{assessment.assessment}")
            st.markdown(f"**Plan:**\n{assessment.plan}")

        with details_tab:
            if assessment.differential_diagnosis:
                st.markdown("**Differential Diagnosis:**")
                for dx in assessment.differential_diagnosis:
                    st.markdown(f"- {dx}")
            if assessment.recommended_workup:
                st.markdown("**Recommended Workup:**")
                for item in assessment.recommended_workup:
                    st.markdown(f"- {item}")
            if assessment.urgency:
                urgency_colors = {
                    "routine": "green",
                    "urgent": "orange",
                    "emergent": "red",
                }
                color = urgency_colors.get(assessment.urgency, "gray")
                st.markdown(f"**Urgency:** :{color}[{assessment.urgency.upper()}]")
            if assessment.confidence > 0:
                st.markdown(f"**Confidence:** {assessment.confidence:.0%}")

        with st.expander("Raw Output"):
            st.code(assessment.raw_output, language=None)


def render_patient_report(report: PatientReport) -> None:
    """Render patient-friendly report in an expandable section."""
    with st.expander("Agent 3: Patient Report", expanded=True):
        if report.summary:
            st.markdown(f"### Summary\n{report.summary}")
        if report.what_we_found:
            st.markdown(f"### What We Found\n{report.what_we_found}")
        if report.what_it_might_mean:
            st.markdown(f"### What It Might Mean\n{report.what_it_might_mean}")
        if report.next_steps:
            st.markdown(f"### Next Steps\n{report.next_steps}")
        if report.questions_to_ask:
            st.markdown("### Questions to Ask Your Doctor")
            for q in report.questions_to_ask:
                st.markdown(f"- {q}")
        if report.flesch_kincaid_grade > 0:
            st.caption(
                f"Readability: Flesch-Kincaid Grade Level {report.flesch_kincaid_grade:.1f}"
            )

        st.info(report.disclaimer)

        with st.expander("Raw Output"):
            st.code(report.raw_output, language=None)


def build_patient_context() -> PatientContext:
    """Build a PatientContext from the sidebar form inputs."""
    st.sidebar.markdown("## Patient Context")

    age = st.sidebar.text_input("Age", placeholder="e.g., 45")
    sex = st.sidebar.selectbox("Sex", ["", "Male", "Female", "Other"])
    chief_complaint = st.sidebar.text_input(
        "Chief Complaint", placeholder="e.g., growing mole on left arm"
    )
    hpi = st.sidebar.text_area(
        "History of Present Illness",
        placeholder="e.g., Lesion noticed 3 months ago, has been increasing in size...",
        height=100,
    )
    pmh = st.sidebar.text_input(
        "Past Medical History", placeholder="e.g., hypertension, diabetes"
    )
    medications = st.sidebar.text_input(
        "Medications", placeholder="e.g., metformin 500mg, lisinopril 10mg"
    )
    allergies = st.sidebar.text_input(
        "Allergies", placeholder="e.g., penicillin, sulfa drugs"
    )
    additional_notes = st.sidebar.text_area(
        "Additional Notes",
        placeholder="Any other relevant information...",
        height=80,
    )

    return PatientContext(
        age=age,
        sex=sex if sex else "",
        chief_complaint=chief_complaint,
        history_of_present_illness=hpi,
        past_medical_history=pmh,
        medications=medications,
        allergies=allergies,
        additional_notes=additional_notes,
    )


# --- Main application ---


def main() -> None:
    """Launch the MedLens Streamlit application."""
    st.title("MedLens")
    st.markdown(
        "**3-Agent Clinical Image Analysis** — Powered by MedGemma 4B"
    )

    render_disclaimer()

    # --- Sidebar: Patient context form ---
    patient_context = build_patient_context()

    # --- Main area: Image upload ---
    st.markdown("---")
    st.markdown("### Upload Clinical Image")

    uploaded_file = st.file_uploader(
        "Choose a clinical image to analyze",
        type=["png", "jpg", "jpeg", "bmp", "tiff"],
        help="Upload a dermatological or clinical image for analysis.",
    )

    clinical_context = st.text_input(
        "Brief clinical context for image (optional)",
        placeholder="e.g., left forearm lesion, present for 3 months",
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(image, caption="Uploaded Image", use_container_width=True)
        with col2:
            st.markdown("**File:** " + uploaded_file.name)
            st.markdown(f"**Size:** {image.size[0]} x {image.size[1]} px")

    st.markdown("---")

    # --- Analyze button ---
    analyze_disabled = uploaded_file is None
    analyze_clicked = st.button(
        "Analyze Image",
        type="primary",
        disabled=analyze_disabled,
        use_container_width=True,
    )

    if analyze_clicked and uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")

        # Load model and create orchestrator
        with st.spinner("Loading model..."):
            model = load_model()
        orchestrator = MedLensOrchestrator(model)

        # Run pipeline with progress display via callback
        progress_bar = st.progress(0, text="Starting pipeline...")

        def on_progress(stage: str, fraction: float, message: str) -> None:
            progress_bar.progress(int(fraction * 100), text=message)

        result = orchestrator.run(
            image=image,
            patient_context=patient_context,
            clinical_context=clinical_context,
            on_progress=on_progress,
        )

        if not result.success:
            logger.exception("Pipeline error: %s", result.error)

        # --- Display results ---
        if result.success:
            st.success(f"Analysis complete in {result.total_time:.1f}s")

            # Sidebar metrics
            render_sidebar_metrics(result)

            # Agent outputs
            if result.visual_findings:
                render_visual_findings(result.visual_findings)
            if result.clinical_assessment:
                render_clinical_assessment(result.clinical_assessment)
            if result.patient_report:
                render_patient_report(result.patient_report)

        else:
            st.error(f"Pipeline failed: {result.error}")

    elif not analyze_clicked:
        st.info("Upload a clinical image and click **Analyze Image** to begin.")


if __name__ == "__main__":
    main()
