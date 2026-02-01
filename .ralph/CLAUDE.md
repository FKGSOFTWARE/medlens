# Opti-Ralph v2 Project — MedLens

You are operating in an **Opti-Ralph loop** building **MedLens**, a 3-agent
clinical assistant for the MedGemma Impact Challenge.

## Core Principle

**State persists ONLY in files. You have NO memory between iterations.**

Trust files. Read before acting. Write before ending.

## Project Context

### What is MedLens?
MedLens is a point-of-care clinical decision support tool that uses MedGemma 4B
(multimodal) to analyze clinical images alongside patient context. It produces
structured clinical assessments (SOAP notes) and patient-friendly reports through
a 3-agent agentic pipeline.

### The 3-Agent Pipeline
1. **Visual Analysis Agent** (`src/medlens/agents/visual.py`): Takes a clinical
   image, runs MedGemma multimodal inference, outputs structured findings JSON
   (morphology, location, severity, descriptors).
2. **Clinical Reasoning Agent** (`src/medlens/agents/reasoning.py`): Takes visual
   findings + patient context (age, history, symptoms), produces differential
   diagnosis, recommended workup, urgency assessment, SOAP note.
3. **Patient Report Agent** (`src/medlens/agents/report.py`): Takes clinical
   output, converts to plain-language patient handout at Flesch-Kincaid grade
   level 6-8.

### Key Technical Details
- **Model**: MedGemma 4B multimodal (`google/medgemma-4b-it` from HuggingFace)
- **Quantization**: 4-bit via bitsandbytes (fits in 16GB VRAM)
- **Framework**: transformers + accelerate + bitsandbytes
- **Frontend**: Streamlit
- **Hardware target**: NVIDIA RTX 4070 Ti Super (16GB VRAM)
- **Python**: 3.10+

### Architecture Decisions
- Single model loaded once, shared across all 3 agents (not 3 separate loads)
- Orchestrator (`src/medlens/orchestrator.py`) manages the pipeline flow
- Model loading/inference abstracted in `src/medlens/model.py`
- Each agent is a class with a `run()` method that takes typed inputs and returns typed outputs
- All agent outputs are structured (dataclasses or TypedDict) for pipeline composability

### Medical AI Disclaimers
- This is a DECISION SUPPORT tool, not a diagnostic tool
- All outputs must include disclaimers that this is not medical advice
- Never claim the system replaces physician judgment
- Frame everything as "assistive" and "supportive"

## File Locations

| File | Purpose | Access |
|------|---------|--------|
| `.ralph/brief.md` | Goal - what success looks like | Read |
| `.ralph/context.md` | Research synthesis | Read/Write |
| `.ralph/plan.md` | Strategy + task list | Read/Write |
| `.ralph/progress.md` | Execution log | Append |
| `.ralph/learnings.md` | Failure knowledge | Read/Append |
| `.ralph/state.json` | Current phase, iteration | Read |
| `.ralph/config.json` | Settings, thresholds | Read |

## Natural Language Tool Calling

**Project Standard**: Describe tool actions in plain English instead of structured JSON.

### Quick Reference

| Action | Natural Language Pattern |
|--------|-------------------------|
| Read file | "Read the file /path/to/file to understand X" |
| Write file | "Create a new file at /path/to/file with the following content: ..." |
| Edit file | "In /path/to/file, replace X with Y" |
| Search code | "Search for pattern X in /path/to/directory" |
| Find files | "Find all files matching *.py in /path/to/directory" |
| Run command | "Run command X in /path/to/directory" |
| Git status | "Run 'git status' to check working directory state" |

## The Loop

```
┌─────────────────┐
│  UNDERSTAND     │  Research the codebase and requirements
└────────┬────────┘
         ▼
┌─────────────────┐
│     PLAN        │  Strategy + task decomposition
└────────┬────────┘
         ▼
┌─────────────────┐
│    EXECUTE      │  ReAct loop: Reason → Act → Reflect → Verify → Adapt
└────────┬────────┘
         ▼
      [DONE]
```

## Signals

Output these to communicate with the loop controller:

```xml
<phase name="understand" status="complete"/>
<phase name="plan" status="complete"/>
<task id="task-id" status="in_progress"/>
<task id="task-id" status="complete"/>
<task id="task-id" status="failed" reason="why"/>
<done/>
<stop reason="explanation"/>
<checkpoint reason="explanation"/>
<uncertainty level="0.8" reason="..."/>
<scope_change reason="discovered X"/>
```

## Available Systems

| System | Purpose |
|--------|---------|
| **Verification** | External checks (tests, linter, types) run after each task |
| **Escalation** | Detects frustration/failure patterns and escalates to human |
| **Skills** | Domain skill libraries injected via `{{SKILLS}}` placeholder |
| **Memory** | Segment-level memory persisted across sessions |
| **Baseline** | Rolling performance baselines with anomaly detection |
| **Self-improvement** | Patterns from past successes injected via `{{SUCCESSFUL_PATTERNS}}` |
| **LATS** | Tree search for complex tasks with high uncertainty |

## Rules

1. **Read first**: Always read `.ralph/learnings.md` and `.ralph/brief.md` before acting
2. **One task at a time**: Focus on single task per iteration
3. **Reflect before verify**: Pause to question your work before checking it
4. **Verify immediately**: Check your work before moving on
5. **Log everything**: Append to `.ralph/progress.md` each iteration
6. **Fail fast**: If stuck after 2 attempts, signal for help
7. **No memory**: If it's not in a file, you don't know it
