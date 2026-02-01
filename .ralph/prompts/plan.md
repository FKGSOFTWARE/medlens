# Plan Phase

> You are in the PLAN phase of an Opti-Ralph loop.
> Your job: Create a strategy and task list based on research.

## Current State
- **Phase:** {{PHASE}}
- **Scale:** {{SCALE}}
- **Mode:** {{MODE}}

## Your Mission

Transform research into an actionable plan:
1. Choose an approach (strategy)
2. Break it into tasks (decomposition)
3. Identify risks and verification steps

## Steps

### 1. Read Context

```
Read the brief file at .ralph/brief.md to understand the goal and success criteria
Read .ralph/context.md to review the research findings and identified approaches
Read .ralph/learnings.md to understand past failures and what to avoid
```

### 2. Choose Strategy

Based on research, decide:
- Which approach from context.md?
- Why this approach over alternatives?
- What are the risks?

Write a 1-2 paragraph strategy in `.ralph/plan.md`.

### 3. Decompose into Tasks

Break the strategy into discrete tasks. **Write tasks as natural language actions that can be directly executed.**

**Good tasks are:**
- Small enough to complete in one iteration
- Independently verifiable
- Ordered by dependency (do X before Y)
- Written as actionable statements (describe the action, not just the topic)

**Task format in plan.md:**
```markdown
## Tasks

1. [ ] Update the login handler in src/auth/login.py to validate email format before authentication
2. [ ] Add error handling to the database connection in src/db/connection.py for timeout scenarios
3. [ ] Create unit tests in tests/test_auth.py covering the new email validation logic
```

**Examples of task phrasing:**

| Bad (topic-only) | Good (natural language action) |
|------------------|-------------------------------|
| "Email validation" | "Update the login handler to validate email format" |
| "Error handling" | "Add try/catch blocks to handle database connection failures" |
| "Tests" | "Create unit tests for the authentication module covering edge cases" |
| "Refactor auth" | "Refactor the authenticate function to separate password hashing from user lookup" |

**Guidelines by scale:**
- **Simple**: 1-3 tasks, flat list
- **Medium**: 3-10 tasks, may have dependencies
- **Complex**: 5-15 tasks, grouped by zone/area

### 4. Identify Risks

For each significant risk:
- What could go wrong?
- How will we detect it?
- How will we mitigate?

### 5. Define Verification

How will we know the goal is achieved?
- Tests to run
- Behavior to verify
- Criteria from brief.md to check

### 5.5 Reflect on Plan

Before signaling completion, pause and answer:

**1. Is this plan achievable?**
- Are tasks appropriately sized (~1 iteration each)?
- Are dependencies correctly ordered?
- Are there hidden assumptions?

**2. What could go wrong?**
- Which tasks have the highest uncertainty?
- Where might scope creep in?
- What if the chosen approach doesn't work?

**3. Is verification adequate?**
- Can every task be independently verified?
- Are success criteria measurable?
- Do verification steps match the brief?

If reflection reveals the plan is weak or risky, revise before signaling complete.

### 6. Signal Completion

When plan is ready:
```xml
<phase name="plan" status="complete"/>
```

If task is too complex to plan:
```xml
<uncertainty level="0.9" reason="Task scope too large, recommend splitting goal"/>
<stop reason="Suggest breaking this into multiple briefs"/>
```

## Output Format

Update `.ralph/plan.md` with:
1. **Approach**: 1-2 paragraph strategy
2. **Tasks**: Ordered checkbox list (written as natural language actions)
3. **Files to Modify**: Quick reference
4. **Risks**: Table of risk/mitigation
5. **Verification**: How we'll know it works

End with signal.

## Rules

- **Don't over-plan**: Tasks should be ~1 iteration each
- **Flat is better**: Avoid deep nesting unless truly needed
- **Order matters**: Put dependencies first
- **Include verification**: Each task should be checkable
- **Stay focused**: Only tasks that achieve the brief
- **Write actionable tasks**: Each task should read as a natural language instruction that can be directly executed

## Anti-patterns

- Creating 20+ tasks (too granular)
- Tasks like "research X" (that's done)
- Tasks without clear completion criteria
- Parallel tasks with hidden dependencies
- Topic-only tasks like "Authentication" instead of "Update the auth handler to..."
