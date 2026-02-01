# MedLens — Project Context

## What Is This?
MedLens is a 3-agent agentic clinical assistant for the MedGemma Impact Challenge.
It uses MedGemma 4B multimodal to analyze clinical images + patient context and
produce structured clinical assessments and patient-friendly reports.

## Tech Stack
- Python 3.10+
- MedGemma 4B (`google/medgemma-4b-it`) via HuggingFace transformers
- 4-bit quantization via bitsandbytes
- Streamlit for UI
- Runs on NVIDIA RTX 4070 Ti Super (16GB VRAM)

## Project Layout
```
src/medlens/
├── agents/
│   ├── visual.py      # Agent 1: Image → structured findings
│   ├── reasoning.py   # Agent 2: Findings + context → SOAP note
│   └── report.py      # Agent 3: Clinical output → patient report
├── orchestrator.py    # Chains the 3 agents
├── model.py           # MedGemma loading/inference
└── app.py             # Streamlit frontend
```

## Key Conventions
- Each agent is a class with a `run()` method
- Agent inputs/outputs are typed (dataclasses)
- Single model instance shared across agents via `model.py`
- All clinical outputs include disclaimers — this is decision support, not diagnosis
- Config lives in `configs/model_config.yaml`

## Running
```bash
# Setup
bash scripts/setup_env.sh
bash scripts/download_model.sh

# Run app
streamlit run src/medlens/app.py

# Tests
pytest tests/
```

## Competition
- MedGemma Impact Challenge on Kaggle
- Deadline: Feb 24, 2026 11:59 PM UTC
- Requires: public GitHub repo, 3-min video, 3-page writeup
