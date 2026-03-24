# AGENTS.md — Sustainability ROI Calculator

Operational guide for AI agents working on this repository.

## Repository Layout

```text
pipeline/    Python analytics pipeline module
tests/       pytest test suite
data/        Input data and generated outputs
docs/        Project documentation
```

## Mandatory Workflow

### Before any code change

1. Read the relevant instruction file from `.github/instructions/`
2. Identify the verification gate for the layer being changed
3. Plan using the `plan-execute-verify` skill

### After any code change

1. Run the verification gate for the changed layer
2. Run `get_errors` on all modified files
3. Fix all errors before reporting done

## Verification Gates

### Python

```bash
ruff check . --config pyproject.toml
black --check --config pyproject.toml .
pytest tests -q
```

### Pipeline Smoke Test

```bash
python -m pipeline.runner
```

## Security Rules (blocking)

- No `os.environ.get("VAR", "fallback")` for secrets — raise `RuntimeError`
- No credentials in source code
- No hardcoded production file paths

## CI / Standards Governance

The `standards-governance` job in `.github/workflows/python-app.yml` enforces:

- All 12 standards baseline files present
- Security pattern scan

## Skills Available

| Skill | Path |
|---|---|
| Plan -> Execute -> Verify | `.github/skills/plan-execute-verify/SKILL.md` |
| Standards Review | `.github/skills/standards-review/SKILL.md` |
