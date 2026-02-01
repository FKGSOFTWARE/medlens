# Understand Phase

> You are in the UNDERSTAND phase of an Opti-Ralph loop.
> Your job: Research the codebase to build context for the task.

## Current State
- **Phase:** {{PHASE}}
- **Scale:** {{SCALE}}
- **Mode:** {{MODE}}

## Your Mission

Read `.ralph/brief.md` to understand the goal, then research the codebase to answer:

1. **What exists?** - Current implementation relevant to this task
2. **What patterns?** - How similar things are done in this codebase
3. **What constraints?** - Technical limitations, dependencies, gotchas
4. **What approach?** - Recommended way to achieve the goal

## Steps

### 1. Read the Brief

Read the file .ralph/brief.md to understand what success looks like.

### 2. Read Learnings

Read the file .ralph/learnings.md to know what to avoid from previous failures.

### 3. Research the Codebase

Search for relevant code using natural language. Examples:

- "Search for all Python files that import the auth module"
- "Find files matching the pattern src/**/*.ts"
- "Look for functions containing 'async def' in the handlers directory"
- "Search for 'TODO' or 'FIXME' comments in the codebase"
- "Find all test files that test the database module"

Read files to understand implementation:

- "Read the main configuration file to understand settings"
- "Read the user model to understand the data structure"
- "Read lines 50-100 of the utils file to examine the parse function"

**Be efficient.** Don't read everything. Target your searches.

### 4. Write Context

Update `.ralph/context.md` with your findings:
- Current state of relevant code
- Key files to read/modify
- Patterns to follow
- Constraints discovered
- Options considered with tradeoffs
- Your recommendation

### 5. Signal Completion

If research is complete:
```xml
<phase name="understand" status="complete"/>
```

If you need clarification from the user:
```xml
<uncertainty level="0.8" reason="unclear whether X or Y"/>
<stop reason="Need clarification on..."/>
```

If the task is trivial and needs no research:
```xml
<phase name="understand" status="complete"/>
<!-- Note: Skipped detailed research - task is straightforward -->
```

## Output Format

Your response should:
1. Show key findings (brief, not exhaustive)
2. Update `.ralph/context.md` with structured synthesis
3. End with appropriate signal

## Rules

- **Minimum viable research**: Don't over-research simple tasks
- **Search, don't read everything**: Use natural language searches to find relevant files, then read specific ones
- **Focus on the goal**: Only research what's relevant to `.ralph/brief.md`
- **Capture gotchas**: Anything surprising goes in context.md
