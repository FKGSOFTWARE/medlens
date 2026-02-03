# MedLens

**3-Agent Clinical Image Analysis powered by MedGemma 4B**

MedLens is an agentic clinical decision support tool that analyzes clinical images alongside patient context to produce structured clinical assessments and patient-friendly reports. Built for the [MedGemma Impact Challenge](https://kaggle.com/competitions/med-gemma-impact-challenge).

> **Disclaimer:** MedLens is for informational and educational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment.

---

## Architecture

```
                         ┌─────────────────────┐
                         │   Clinical Image     │
                         │   + Patient Context   │
                         └──────────┬────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │   Agent 1: Visual Analysis     │
                    │   MedGemma 4B multimodal       │
                    │   Image → Structured Findings  │
                    └───────────────┬───────────────┘
                                    │  VisualFindings
                    ┌───────────────▼───────────────┐
                    │   Agent 2: Clinical Reasoning  │
                    │   MedGemma 4B text             │
                    │   Findings + Context → SOAP    │
                    └───────────────┬───────────────┘
                                    │  ClinicalAssessment
                    ┌───────────────▼───────────────┐
                    │   Agent 3: Patient Report      │
                    │   MedGemma 4B text             │
                    │   Clinical → Plain Language    │
                    └───────────────┬───────────────┘
                                    │  PatientReport
                         ┌──────────▼────────────┐
                         │   Streamlit Frontend   │
                         │   Interactive Results  │
                         └────────────────────────┘
```

Each agent is a class with a typed `run()` method. A single MedGemma model instance is shared across all agents. The orchestrator chains them with progress callbacks and timing metrics.

---

## Quickstart

### Prerequisites

- Python 3.10+
- NVIDIA GPU with 12+ GB VRAM (tested on RTX 4070 Ti Super, 16 GB)
- CUDA toolkit
- HuggingFace account with access to [google/medgemma-4b-it](https://huggingface.co/google/medgemma-4b-it)

### Setup

```bash
# Clone the repository
git clone https://github.com/<your-org>/medlens.git
cd medlens

# Run environment setup (validates Python, CUDA, installs deps)
bash scripts/setup_env.sh

# Download MedGemma model (requires HuggingFace auth)
bash scripts/download_model.sh

# Launch the app
streamlit run src/medlens/app.py
```

### Docker

```bash
# Build and run with GPU support
docker compose up --build

# App available at http://localhost:8501
```

---

## Project Structure

```
src/medlens/
├── agents/
│   ├── parsing.py     # Shared LLM output parsing utilities
│   ├── visual.py      # Agent 1: Image → structured findings
│   ├── reasoning.py   # Agent 2: Findings + context → SOAP note
│   └── report.py      # Agent 3: Clinical output → patient report
├── orchestrator.py    # Chains the 3 agents with progress callbacks
├── model.py           # MedGemma loading/inference (4-bit quantized)
├── evaluate.py        # Benchmarking and evaluation utilities
└── app.py             # Streamlit frontend
configs/
└── model_config.yaml  # Model and hardware configuration
scripts/
├── setup_env.sh       # Environment validation and setup
└── download_model.sh  # MedGemma model download
tests/
└── test_agents.py     # 39 tests covering all agents and parsing
```

---

## How It Works

1. **Upload** a clinical image (dermatological, wound, etc.) via the Streamlit interface.
2. **Enter** patient context in the sidebar (age, sex, chief complaint, history, medications).
3. **Click Analyze** — the 3-agent pipeline runs sequentially:
   - **Visual Analysis** uses MedGemma's multimodal capabilities to describe morphology, location, severity, color, borders, and size.
   - **Clinical Reasoning** integrates those findings with patient context to produce a SOAP note, differential diagnosis, recommended workup, and urgency assessment.
   - **Patient Report** converts the clinical output into plain language (targeting Flesch-Kincaid grade 6-8) with suggested questions for the patient's doctor.
4. **Review** results at each stage — all intermediate outputs are visible and expandable.

---

## Technical Details

| Component | Detail |
|-----------|--------|
| Model | MedGemma 4B (`google/medgemma-4b-it`) |
| Quantization | 4-bit NF4 via bitsandbytes (double quantization) |
| VRAM | ~6-8 GB loaded (fits 12+ GB GPUs) |
| Framework | HuggingFace transformers + accelerate |
| Frontend | Streamlit |
| Python | 3.10+ |

---

## Testing

```bash
pytest tests/ -v
```

39 tests covering data structures, output parsing (structured, unstructured, edge cases), prompt building, Flesch-Kincaid computation, confidence/urgency normalization.

---

## Competition

- **Challenge:** [MedGemma Impact Challenge](https://kaggle.com/competitions/med-gemma-impact-challenge)
- **Track:** Main Track + Agentic Workflow Prize
- **Deadline:** February 24, 2026

---

## License

MIT
