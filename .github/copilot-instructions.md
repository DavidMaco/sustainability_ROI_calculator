# Sustainability ROI Calculator — Copilot Instructions

Python analytics tool for calculating sustainability ROI metrics across
materials and procurement scenarios. Python 3.12, `pipeline/` module, ruff + black.

## Verification Gates

```bash
ruff check . --config pyproject.toml
black --check --config pyproject.toml .
pytest tests -q
```

### Pipeline Smoke Test

```bash
python -m pipeline.runner
```

## Security Standards (non-negotiable)

- **Never** add `os.environ.get("VAR", "fallback-secret")` — raise `RuntimeError` if missing
- No secrets or credentials in source code
- No hardcoded file paths to production data

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
