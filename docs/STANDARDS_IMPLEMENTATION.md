# Sustainability ROI Calculator Standards Implementation

## Scope

This document defines implemented standards for this repository.

## Implemented Standards

### 1. Execution Workflow Standard

Implemented via `.github/instructions/execution-workflow.instructions.md`
and `.github/skills/plan-execute-verify/SKILL.md`.

Key rules:

- Plan-first for non-trivial tasks
- Mandatory verification before completion

### 2. Python Application Standard

Implemented via `.github/instructions/api-ops.instructions.md`.

Key rules:

- Typed output structures from public functions
- Empty and malformed input handling
- Parameterized configuration, no bare `os.environ`

### 3. Output Quality Standard

Implemented via `.github/instructions/frontend-quality.instructions.md`.

Key rules:

- Consistent column naming in all CSV outputs
- Human-readable report format

### 4. Security Review Standard

Implemented via `.github/instructions/security.instructions.md`
and `.github/skills/standards-review/SKILL.md`.

Key rules:

- No hardcoded fallback secrets
- CI-enforced pattern scan

### 5. Documentation Standard

Implemented via `.github/instructions/documentation.instructions.md`.

Key rules:

- Conventional commits, one logical change per commit
