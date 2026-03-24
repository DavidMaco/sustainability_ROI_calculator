# Plan -> Execute -> Verify

**Skill domain:** Structured change execution for the Sustainability ROI Calculator.

## When to Use

Use whenever a task involves more than a single-line edit:

- Adding new ROI calculation methods or pipeline stages
- Changing output formats or data schemas
- Modifying environment configuration
- CI/CD pipeline modifications

## Protocol

### Step 1 — Plan

```
Files to change: [list]
Tests to run: [list of commands]
Risk of regression: [low | medium | high]
Sub-tasks: [numbered list]
```

### Step 2 — Execute

- Change one concern at a time
- Read files before editing
- Apply security standards throughout

### Step 3 — Verify

| Layer | Commands |
|---|---|
| Python | `ruff check . && black --check . && pytest tests -q` |
| Pipeline | `python -m pipeline.runner` |

Then run `get_errors` on every modified file.

### Step 4 — Complete

Mark each todo complete immediately after verification.

## Discipline Constraints

- Never mark a step complete if errors remain
- One pull request = one logical concern
