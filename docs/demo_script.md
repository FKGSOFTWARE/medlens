# MedLens Demo Video Script

**Target length:** 3 minutes max  
**Format:** Screen recording with voiceover

---

## 0:00–0:15 — Title & Hook

**[SCREEN: MedLens logo / title card]**

> "Clinical documentation takes up to 50% of a physician's day, while 88% of patients struggle to understand their medical results. MedLens solves both problems with a 3-agent AI pipeline powered by MedGemma."

---

## 0:15–0:45 — The Problem

**[SCREEN: Split view — physician buried in paperwork / confused patient reading medical report]**

> "When a doctor examines a suspicious skin lesion, they must: analyze the image, document findings, reason through differentials, write a clinical note, AND explain it to the patient in plain language. Each step requires a different cognitive mode."

> "MedLens automates this with three specialized AI agents — each handling one part of the workflow — running on a single GPU."

---

## 0:45–1:00 — Architecture Overview

**[SCREEN: Architecture diagram from README]**

> "Agent 1 uses MedGemma's multimodal vision to describe what it sees — morphology, color, borders, severity. Agent 2 integrates those findings with patient history to produce a SOAP note and differential diagnosis. Agent 3 converts the clinical output into plain language a patient can understand — targeting a 6th to 8th grade reading level."

---

## 1:00–2:30 — Live Demo

**[SCREEN: Streamlit app]**

### Upload Image (1:00–1:10)
> "Let's see it in action. I'll upload an image of a pigmented lesion..."

**[ACTION: Upload image, show preview]**

### Enter Patient Context (1:10–1:25)
> "...and enter some patient context: 52-year-old male, noticed this mole 6 months ago, it's been changing. History of diabetes and hypertension."

**[ACTION: Fill sidebar form]**

### Run Pipeline (1:25–1:45)
> "Now I click Analyze, and watch the three agents work in sequence..."

**[ACTION: Click button, show progress bar moving through agents]**

### Review Visual Findings (1:45–1:55)
> "Agent 1 found an asymmetric lesion with irregular borders, color variegation including blue-black pigment, about 8 millimeters. Confidence 90%."

**[ACTION: Expand Agent 1 section]**

### Review Clinical Assessment (1:55–2:10)
> "Agent 2 produced a full SOAP note. The assessment flags this as concerning per ABCDE criteria, recommends urgent dermatology referral, and lists the differential — dysplastic nevus, possible melanoma, and others."

**[ACTION: Expand Agent 2 section, show SOAP tab and Details tab]**

### Review Patient Report (2:10–2:30)
> "Agent 3 converted that into language the patient can understand: 'There is a dark spot on your arm... it has uneven edges and several different colors...' Notice the Flesch-Kincaid grade of 7.2 — right in our target range. And suggested questions for the patient to ask their doctor."

**[ACTION: Expand Agent 3 section, highlight FK score and questions]**

---

## 2:30–2:50 — Technical Highlights

**[SCREEN: Sidebar metrics + code structure]**

> "Total pipeline time: 16 seconds on an RTX 4070 Ti. MedGemma 4B running at 4-bit quantization uses only 6.8 gigs of VRAM. All intermediate outputs are observable — the clinician can catch errors at any stage. 39 tests cover the parsing and data structures."

---

## 2:50–3:00 — Closing

**[SCREEN: GitHub repo + disclaimer]**

> "MedLens: three agents, one model, bridging clinical documentation and patient comprehension. Code is open source. Thanks for watching."

**[SCREEN: Disclaimer — "MedLens is for informational purposes only. Not a substitute for professional medical advice."]**

---

## Recording Notes

1. **Pre-run the demo once** to warm up model (first load is slower)
2. **Use the dermatology sample case** from `examples/sample_output_dermatology.json`
3. **Prepare a matching sample image** — use a public domain dermoscopy image from ISIC or similar
4. **OBS settings:** 1080p, 30fps, record system audio + mic
5. **Post-editing:** Add title cards, trim pauses, add captions
