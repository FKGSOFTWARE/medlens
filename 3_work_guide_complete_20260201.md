# Iteration 3 — Work Guide (Complete) — 2026-02-01

## Scope

Resolve all deviations from optimality identified during post-iteration-2 audit.
12 issues across 4 severity tiers (2 critical, 2 high, 4 medium, 4 low).

---

## Issues Resolved

### CRITICAL

#### 1. 12/39 tests failing — `_parse_output` called with `None` as `self`

**Root cause:** `_parse_output` is an instance method that calls `self._extract_section()`,
but tests invoke it as `Agent._parse_output(None, text)`. `None._extract_section` raises
`AttributeError`.

**Fix:** Made `_parse_output` a `@staticmethod` in all 3 agents (`visual.py`, `reasoning.py`,
`report.py`). Internal calls now go through the shared `parsing.py` module functions
instead of `self.method()`. Updated all tests to call `Agent._parse_output(text)` (1 arg).

**Files:** `src/medlens/agents/visual.py`, `reasoning.py`, `report.py`, `tests/test_agents.py`

#### 2. Build backend broken — `setuptools.backends._legacy:_Backend` doesn't exist

**Root cause:** `pyproject.toml` specified a non-existent build backend module.

**Fix:** Changed to `setuptools.build_meta`.

**Files:** `pyproject.toml:3`

---

### HIGH

#### 3. Type error — `PatientReport.questions_to_ask: list[str] = None`

**Root cause:** Annotation says `list[str]` but default is `None`. mypy error.
Runtime hack via `__post_init__` masked the issue.

**Fix:** Changed to `questions_to_ask: list[str] = field(default_factory=list)`.
Removed the `__post_init__` workaround entirely.

**Files:** `src/medlens/agents/report.py:33-35`

#### 4. Silent bug — `max_new_tokens or self.config.max_new_tokens`

**Root cause:** `or` treats `0` as falsy, silently falling through to config default.
Inconsistent with `temperature` handling which correctly uses `is not None`.

**Fix:** Changed to `max_new_tokens if max_new_tokens is not None else self.config.max_new_tokens`.

**Files:** `src/medlens/model.py:200-203`

---

### MEDIUM

#### 5. Code duplication — parsing functions copy-pasted across 3 agents

**Root cause:** `_extract_section`, `_extract_list`, `_parse_confidence` were
verbatim duplicates across `visual.py`, `reasoning.py`, `report.py`.

**Fix:** Created `src/medlens/agents/parsing.py` with shared functions:
`extract_section`, `extract_list`, `parse_confidence`, `parse_urgency`.
All agents import from this module. Added `TestSharedParsing` test class.

**Files:** `src/medlens/agents/parsing.py` (new), all 3 agent files, `tests/test_agents.py`

#### 6. `app.py` duplicates orchestrator pipeline logic

**Root cause:** `app.py` manually ran all 3 agents with inline timing/progress,
duplicating `orchestrator.py:79-97`. Any pipeline change needed 2-place edits.

**Fix:** Added `on_progress: ProgressCallback | None` parameter to
`orchestrator.run()`. App now calls `orchestrator.run(on_progress=callback)`
and the callback drives the Streamlit progress bar. Single source of truth.

**Files:** `src/medlens/orchestrator.py`, `src/medlens/app.py`

#### 7. Orchestrator `model` param untyped

**Fix:** Added `model: MedGemmaModel` type annotation.

**Files:** `src/medlens/orchestrator.py:55`

#### 8. Dead YAML config — `agents:` section never read

**Root cause:** `from_yaml()` only reads `model:` section. Per-agent configs
are hardcoded class constants. The YAML `agents:` block was dead config.

**Fix:** Removed the dead `agents:` section from `configs/model_config.yaml`.

**Files:** `configs/model_config.yaml`

---

### LOW

#### 9. 13 mypy errors in `model.py`

**Root cause:** `_model`/`_processor` initialized as `None` without type narrowing.
Various `dict` type mismatches.

**Fix:** Typed as `Any`, extracted `_ensure_loaded()` guard method, typed
`messages` and `kwargs` as `dict[str, Any]`. Reduced from 13 errors to 1
(external `transformers` stub for `BitsAndBytesConfig`).

**Files:** `src/medlens/model.py`

#### 10. Unused `peft` dependency

**Fix:** Removed from `pyproject.toml` dependencies.

**Files:** `pyproject.toml:28`

#### 11. `ruff` not installed — no linting run

**Status:** `ruff` is in `[project.optional-dependencies] dev` but not in the
environment. Not a code fix — requires `pip install -e '.[dev]'`.

#### 12. Fragile regex parser

**Status:** Documented known limitation. Regex `(?=\n[A-Z][\w\s]*:|$)` can
misfire on content lines starting with uppercase-colon patterns. Accepted risk
with fallback behavior covering failure cases.

---

## Verification Results

| Check       | Before | After  |
|-------------|--------|--------|
| Tests       | 12 FAIL / 27 pass | **39 pass / 0 fail** |
| Compilation | OK | OK |
| mypy        | 13 errors | **1 error** (external stub) |
| Build       | Broken | **Fixed** |

---

## Files Changed

| File | Action |
|------|--------|
| `pyproject.toml` | Fixed build backend, removed peft |
| `src/medlens/agents/parsing.py` | **New** — shared parsing utilities |
| `src/medlens/agents/visual.py` | Refactored to use parsing.py, `_parse_output` → staticmethod |
| `src/medlens/agents/reasoning.py` | Refactored to use parsing.py, `_parse_output` → staticmethod |
| `src/medlens/agents/report.py` | Refactored to use parsing.py, `_parse_output` → staticmethod, fixed type |
| `src/medlens/model.py` | Fixed `or` bug, mypy errors, added `_ensure_loaded()` |
| `src/medlens/orchestrator.py` | Added type hint, `ProgressCallback`, `on_progress` param |
| `src/medlens/app.py` | Uses orchestrator with callback, removed duplicated pipeline |
| `configs/model_config.yaml` | Removed dead `agents:` section |
| `tests/test_agents.py` | Updated for staticmethod signatures, added `TestSharedParsing` |
