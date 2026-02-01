# Brief

## Goal
Build "MedLens" — a 3-agent agentic clinical assistant using MedGemma 4B
multimodal that analyzes clinical images + patient context to produce
structured clinical assessments and patient-friendly reports, for submission
to the MedGemma Impact Challenge (deadline: Feb 24, 2026).

## Success Criteria
- [ ] MedGemma 4B loads quantized (4-bit) and runs inference on RTX 4070 Ti Super (16GB)
- [ ] Visual Analysis Agent: Takes image → produces structured findings JSON
- [ ] Clinical Reasoning Agent: Takes findings + context → produces SOAP note
- [ ] Patient Report Agent: Takes clinical output → produces plain-language summary
- [ ] Orchestrator chains all 3 agents with observable intermediate outputs
- [ ] Streamlit app: Upload image + enter notes → see agent chain → get outputs
- [ ] Latency < 30s total for full 3-agent pipeline
- [ ] Patient report scores Flesch-Kincaid grade level 6-8
- [ ] All code in public GitHub repo
- [ ] 3-minute demo video recorded
- [ ] 3-page writeup completed per competition template
- [ ] Submitted to Kaggle as Writeup before Feb 24 11:59 PM UTC

## Scope
**In scope:**
- MedGemma 4B multimodal inference (quantized)
- 3-agent pipeline (visual → reasoning → patient report)
- Streamlit frontend with image upload
- SOAP-format clinical note output
- Patient-friendly report with health literacy scoring
- Demo on dermatological/wound images
- Competition writeup + video

**Out of scope:**
- Fine-tuning (stretch goal if time permits)
- Multi-language support
- EHR integration
- HIPAA compliance infrastructure
- Mobile deployment
- Real patient data

## Constraints
- Must use MedGemma (HAI-DEF model) — mandatory per competition rules
- Must run on RTX 4070 Ti Super (16GB VRAM)
- Deadline: February 24, 2026 11:59 PM UTC
- Single Kaggle Writeup submission per team
- Video max 3 minutes, writeup max 3 pages
- All code must be in public GitHub repo
