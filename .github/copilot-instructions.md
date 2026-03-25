# Sustainability ROI Calculator — Copilot Instructions

Python analytics tool for calculating sustainability ROI metrics across
materials and procurement scenarios. Python 3.12, `pipeline/` module, ruff + black.

## Mandatory Workflow

1. Plan before editing.
2. Keep changes scoped to root cause.
3. Verify before completion.

## Verification Gates

```bash
ruff check . --config pyproject.toml
black --check --config pyproject.toml .
pytest tests -q
python -m pyright
```

### Pipeline Smoke Test

```bash
python -m pipeline.runner
```

Use only the commands available in this repo environment.

## Security Standards (non-negotiable)

- **Never** add `os.environ.get("VAR", "fallback-secret")` — raise `RuntimeError` if missing
- No secrets or credentials in source code
- No hardcoded file paths to production data
- No raw exception leakage to users
- Keep logging structured and non-sensitive

## Code Standards

### Python

- `from __future__ import annotations` on every module
- Pydantic models or dataclasses for all config structures
- Logger via `logging.getLogger(__name__)`
- All DataFrame operations must handle empty frames gracefully

## Instruction Files

| Scope | File |
|---|---|
| Python Application | `.github/instructions/api-ops.instructions.md` |
| Output & Reporting | `.github/instructions/frontend-quality.instructions.md` |
| Security | `.github/instructions/security.instructions.md` |
| Documentation | `.github/instructions/documentation.instructions.md` |
| Workflow | `.github/instructions/execution-workflow.instructions.md` |
