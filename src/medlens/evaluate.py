"""Evaluation and benchmarking utilities for MedLens pipeline.

Provides functions for measuring pipeline performance, readability
scoring, and generating evaluation reports. Used for competition
writeup metrics and ongoing quality monitoring.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from medlens.agents.reasoning import PatientContext
from medlens.agents.report import compute_flesch_kincaid_grade
from medlens.orchestrator import MedLensOrchestrator, PipelineResult

if TYPE_CHECKING:
    from PIL import Image

    from medlens.model import MedGemmaModel

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Metrics from a single pipeline evaluation run."""

    image_path: str = ""
    total_time_s: float = 0.0
    visual_analysis_time_s: float = 0.0
    clinical_reasoning_time_s: float = 0.0
    patient_report_time_s: float = 0.0
    flesch_kincaid_grade: float = 0.0
    fk_target_met: bool = False  # True if grade 6-8
    num_differentials: int = 0
    urgency: str = ""
    visual_confidence: float = 0.0
    clinical_confidence: float = 0.0
    pipeline_success: bool = False
    error: str = ""


def evaluate_single(
    orchestrator: MedLensOrchestrator,
    image: Image.Image,
    patient_context: PatientContext,
    clinical_context: str = "",
    image_path: str = "",
) -> EvaluationResult:
    """Run the pipeline on a single image and collect metrics.

    Args:
        orchestrator: Initialized MedLensOrchestrator.
        image: PIL Image to analyze.
        patient_context: Patient context for this case.
        clinical_context: Optional brief context string.
        image_path: Path to image file (for logging).

    Returns:
        EvaluationResult with all metrics filled.
    """
    result = orchestrator.run(image, patient_context, clinical_context)

    eval_result = EvaluationResult(
        image_path=image_path,
        total_time_s=result.total_time,
        pipeline_success=result.success,
        error=result.error,
    )

    if result.timings:
        eval_result.visual_analysis_time_s = result.timings.get("visual_analysis", 0.0)
        eval_result.clinical_reasoning_time_s = result.timings.get("clinical_reasoning", 0.0)
        eval_result.patient_report_time_s = result.timings.get("patient_report", 0.0)

    if result.visual_findings:
        eval_result.visual_confidence = result.visual_findings.confidence

    if result.clinical_assessment:
        eval_result.num_differentials = len(result.clinical_assessment.differential_diagnosis)
        eval_result.urgency = result.clinical_assessment.urgency
        eval_result.clinical_confidence = result.clinical_assessment.confidence

    if result.patient_report:
        eval_result.flesch_kincaid_grade = result.patient_report.flesch_kincaid_grade
        eval_result.fk_target_met = 6.0 <= result.patient_report.flesch_kincaid_grade <= 8.0

    return eval_result


def evaluate_batch(
    orchestrator: MedLensOrchestrator,
    cases: list[dict],
    output_path: str | Path | None = None,
) -> list[EvaluationResult]:
    """Run the pipeline on multiple cases and collect metrics.

    Args:
        orchestrator: Initialized MedLensOrchestrator.
        cases: List of dicts with keys: image (PIL Image), context (PatientContext),
               clinical_context (str, optional), image_path (str, optional).
        output_path: Optional path to write JSON results.

    Returns:
        List of EvaluationResult for each case.
    """
    from PIL import Image as PILImage

    results = []
    for i, case in enumerate(cases):
        logger.info("Evaluating case %d/%d: %s", i + 1, len(cases), case.get("image_path", ""))
        eval_result = evaluate_single(
            orchestrator=orchestrator,
            image=case["image"],
            patient_context=case.get("context", PatientContext()),
            clinical_context=case.get("clinical_context", ""),
            image_path=case.get("image_path", f"case_{i}"),
        )
        results.append(eval_result)

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump([asdict(r) for r in results], f, indent=2)
        logger.info("Evaluation results written to %s", output_path)

    return results


def summarize_results(results: list[EvaluationResult]) -> dict:
    """Compute summary statistics from evaluation results.

    Returns:
        Dict with aggregate metrics suitable for writeup.
    """
    if not results:
        return {}

    successful = [r for r in results if r.pipeline_success]
    n_total = len(results)
    n_success = len(successful)

    if not successful:
        return {
            "total_cases": n_total,
            "successful_cases": 0,
            "success_rate": 0.0,
        }

    times = [r.total_time_s for r in successful]
    fk_grades = [r.flesch_kincaid_grade for r in successful if r.flesch_kincaid_grade > 0]
    fk_on_target = [r for r in successful if r.fk_target_met]

    return {
        "total_cases": n_total,
        "successful_cases": n_success,
        "success_rate": n_success / n_total,
        "latency_mean_s": sum(times) / len(times),
        "latency_median_s": sorted(times)[len(times) // 2],
        "latency_min_s": min(times),
        "latency_max_s": max(times),
        "latency_under_30s": sum(1 for t in times if t <= 30.0) / len(times),
        "fk_grade_mean": sum(fk_grades) / len(fk_grades) if fk_grades else 0.0,
        "fk_target_rate": len(fk_on_target) / n_success if n_success else 0.0,
        "avg_differentials": (
            sum(r.num_differentials for r in successful) / n_success
        ),
    }


def profile_vram() -> dict:
    """Profile current GPU VRAM usage.

    Returns:
        Dict with VRAM metrics in MB, or empty dict if CUDA unavailable.
    """
    try:
        import torch
        if not torch.cuda.is_available():
            return {}
        return {
            "vram_allocated_mb": torch.cuda.memory_allocated() / 1024 / 1024,
            "vram_reserved_mb": torch.cuda.memory_reserved() / 1024 / 1024,
            "vram_total_mb": torch.cuda.get_device_properties(0).total_memory / 1024 / 1024,
            "gpu_name": torch.cuda.get_device_name(0),
        }
    except Exception:
        return {}
