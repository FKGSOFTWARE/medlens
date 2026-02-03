### MedLens: Agentic Clinical Decision Support with MedGemma

### Team

MedLens Team — software engineers specializing in medical AI applications and clinical workflow design.

### Problem Statement

**The dual burden of clinical documentation and health literacy.**

Physicians spend up to 50% of their workday on documentation (Sinsky et al., *Annals of Internal Medicine*, 2016), directly contributing to burnout — now affecting over 60% of U.S. physicians (AMA, 2023). Meanwhile, only 12% of U.S. adults have proficient health literacy (NAAL, 2006), meaning the vast majority of patients struggle to understand their own medical records and clinical findings.

These problems compound at the point of care: a dermatologist examining a suspicious lesion must simultaneously analyze the image, integrate patient history, document structured findings, and explain results in language the patient can understand. Each of these tasks requires different cognitive modes and communication registers.

**Who is the user?** Primary care physicians and dermatologists conducting visual clinical assessments, and their patients who need to understand results. MedLens transforms a fragmented, time-intensive workflow into a structured pipeline where each step is handled by a specialized AI agent — producing both clinician-grade documentation and patient-accessible reports from a single image upload.

**Impact potential:** If deployed across the ~920 million primary care visits in the U.S. annually (CDC NAMCS), even a conservative 2-minute time savings per visual assessment encounter represents 30+ million hours of reclaimed physician time. On the patient side, converting clinical jargon into grade-level 6-8 language could meaningfully improve comprehension for the 88% of adults below proficient health literacy.

### Overall Solution

MedLens implements a **3-agent agentic pipeline** using MedGemma 4B multimodal — a single model instance serving three distinct clinical roles:

**Agent 1 — Visual Analysis** uses MedGemma's multimodal capabilities (image + text) to produce structured findings: morphology, anatomical location, severity, color descriptors, size, border characteristics, and confidence score. This directly leverages MedGemma's pretraining on clinical images and medical visual question-answering tasks, where it outperforms generic vision-language models on medical benchmarks.

**Agent 2 — Clinical Reasoning** takes the structured findings and integrates them with patient context (demographics, history, medications) using MedGemma's text generation to produce a SOAP note, ranked differential diagnosis, recommended workup, and urgency classification (routine/urgent/emergent). MedGemma's clinical language alignment — trained on medical literature and clinical notes — produces more clinically appropriate reasoning than general-purpose LLMs.

**Agent 3 — Patient Report** converts the clinical output into plain language targeting Flesch-Kincaid grade level 6-8. This agent produces: a brief summary, "what we found" in everyday terms, "what it might mean" without causing alarm, concrete next steps, and suggested questions to ask the doctor. Every report includes an AI disclaimer.

**Why MedGemma?** MedGemma's multimodal architecture is specifically designed for medical image understanding. Its pretraining on medical visual question-answering, clinical text, and biomedical literature makes it uniquely suited for the image-to-clinical-reasoning pipeline. Generic multimodal models lack the domain-specific visual grounding needed for reliable morphological description, while text-only medical models cannot process clinical images. MedGemma bridges both requirements in a single model small enough (4B parameters, 4-bit quantized) to run on consumer-grade GPUs.

**Why agentic?** Decomposing the workflow into three agents with typed interfaces creates observable intermediate outputs. A clinician can review the visual findings before clinical reasoning is applied, catching errors early. Each agent uses optimized generation parameters (lower temperature for factual visual description, higher for natural-language patient communication). The pipeline mirrors the actual clinical workflow: observe → reason → communicate.

### Technical Details

**Architecture:** Single MedGemma 4B instance (`google/medgemma-4b-it`) loaded with 4-bit NF4 quantization via bitsandbytes (double quantization enabled). The model occupies ~6-8 GB VRAM, fitting comfortably on GPUs with 12+ GB. Three agent classes share the model, each with a `run()` method taking typed dataclass inputs and returning typed outputs. An orchestrator chains them with progress callbacks and per-agent timing.

**Stack:** Python 3.10+, HuggingFace transformers + accelerate, bitsandbytes for quantization, Streamlit for the interactive frontend. Docker support for reproducible deployment with GPU passthrough.

**Output parsing:** Agents use structured prompts with explicit section headers. Regex-based extraction parses LLM output into dataclasses with graceful fallbacks for unstructured responses. Shared parsing module eliminates code duplication.

**Performance (estimated on RTX 4070 Ti Super, 16 GB):**

| Metric | Value |
|--------|-------|
| Pipeline latency (3 agents) | ~16-18s total |
| Agent 1 (multimodal) | ~4-5s |
| Agent 2 (text) | ~6-7s |
| Agent 3 (text) | ~5-6s |
| VRAM usage | ~6.8 GB |
| FK grade (patient report) | 7.0-7.8 (target: 6-8) |

**Deployment challenges and mitigations:**
- *VRAM constraints:* 4-bit quantization with double quant reduces memory by ~75% vs. FP16 while maintaining clinical quality.
- *LLM output variability:* Structured prompts + regex parsing with fallbacks handle inconsistent formatting. Low temperature (0.2) for factual visual analysis minimizes hallucination.
- *Latency:* Sequential pipeline targets <30s total. Per-agent generation limits (768-1024 tokens) prevent runaway inference.
- *Clinical safety:* All outputs include disclaimers. The system frames itself as decision support, never as diagnostic.

**Testing:** 39 unit tests covering all agents, parsing logic, data structures, prompt building, confidence/urgency normalization, Flesch-Kincaid computation, and edge cases (empty output, unstructured fallback).

**Source code:** [github.com/your-org/medlens](https://github.com/your-org/medlens)
**Video demo:** [link]

---

*MedLens is a decision-support tool for informational purposes only. It is not intended to replace professional medical judgment.*
