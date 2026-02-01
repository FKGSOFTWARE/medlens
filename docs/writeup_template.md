# MedLens: Agentic Clinical Decision Support with MedGemma

> MedGemma Impact Challenge Submission

## 1. Problem Statement

Clinical documentation consumes up to 50% of physician time (AMA, 2023).
Meanwhile, patients frequently leave appointments without fully understanding
their conditions — health literacy remains a critical gap in healthcare
delivery. MedLens addresses both problems through an agentic AI pipeline that
transforms clinical image analysis into structured documentation and
patient-accessible reports.

## 2. Approach

### Architecture

MedLens implements a 3-agent agentic pipeline using MedGemma 4B multimodal:

1. **Visual Analysis Agent** — Analyzes clinical images using MedGemma's
   multimodal capabilities to produce structured findings (morphology,
   location, severity).

2. **Clinical Reasoning Agent** — Integrates visual findings with patient
   context to generate differential diagnoses, recommended workup, and
   SOAP-format clinical notes.

3. **Patient Report Agent** — Converts clinical output into plain-language
   reports at Flesch-Kincaid grade level 6-8, bridging the health literacy gap.

### Technical Implementation

- **Model**: MedGemma 4B multimodal (`google/medgemma-4b-it`)
- **Quantization**: 4-bit via bitsandbytes (fits in 16GB VRAM)
- **Pipeline**: Sequential 3-agent chain with observable intermediate outputs
- **Frontend**: Streamlit web application
- **Hardware**: NVIDIA RTX 4070 Ti Super (16GB VRAM)

### Use of HAI-DEF Models

[Detail specific MedGemma capabilities leveraged...]

## 3. Results

### Performance Metrics

| Metric | Value |
|--------|-------|
| Pipeline latency | TBD |
| Visual analysis accuracy | TBD |
| FK grade level (patient report) | Target: 6-8 |
| VRAM usage | TBD |

### Demo Cases

[Include representative examples...]

## 4. Impact & Future Work

### Clinical Impact
- Reduces documentation burden
- Improves patient comprehension
- Extends specialist-level visual assessment to primary care

### Future Directions
- LoRA fine-tuning on dermatology datasets (ISIC, Fitzpatrick17k)
- Multi-language patient reports
- EHR integration via FHIR
- Mobile deployment

## 5. Repository & Demo

- **GitHub**: [link]
- **Demo Video**: [link]

---

*MedLens is a decision support tool for informational purposes only.
It is not intended to replace professional medical judgment.*
