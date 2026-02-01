# Plan

> Strategy + task list. Updated by the Plan phase.

## Approach

Build the MedLens 3-agent pipeline bottom-up: start with the model layer (MedGemma loading/inference),
then implement each agent in pipeline order (visual → reasoning → report), then wire up the Streamlit
frontend. Each agent parses LLM output into structured dataclasses. The model uses 4-bit quantization
via bitsandbytes to fit on 16GB VRAM.

## Tasks

1. [x] Project scaffolding (data structures, config, scripts, tests)
2. [x] Implement MedGemmaModel (model.py) — load, generate_multimodal, generate_text, from_yaml
3. [ ] Implement VisualAnalysisAgent.run() — image → structured findings
4. [ ] Implement ClinicalReasoningAgent.run() — findings + context → SOAP note
5. [ ] Implement PatientReportAgent.run() — clinical output → patient report
6. [ ] Implement Streamlit app (app.py) — full UI with image upload, context form, pipeline display

## Files to Modify

- src/medlens/model.py
- src/medlens/agents/visual.py
- src/medlens/agents/reasoning.py
- src/medlens/agents/report.py
- src/medlens/app.py
- tests/test_agents.py (add integration tests)

## Risks

| Risk | Mitigation |
|------|------------|
| MedGemma API changes between transformers versions | Pin transformers version, test import |
| 4-bit quantization OOM on 16GB VRAM | Use device_map="auto", monitor memory |
| LLM output parsing failures | Robust regex parsing with fallbacks |
| Slow inference > 30s target | Profile per-agent, optimize prompts |

## Verification

- `pytest tests/` passes (unit + integration)
- Model loads without OOM (GPU test)
- Each agent produces valid structured output
- Full pipeline runs end-to-end < 30s
- Streamlit app renders and processes uploads
