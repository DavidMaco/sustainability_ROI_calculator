---
applyTo: "pipeline/**"
---

# Python Application Standards — Sustainability ROI Calculator

Standards for the Python analytics pipeline.

## Module Conventions

- `from __future__ import annotations` at the top of every module
- Pydantic models or dataclasses for all structured config and calculation outputs
- All config via settings object; no bare `os.environ` in business logic
- Logging via `logger = logging.getLogger(__name__)`

## Data Processing Standards

- Validate all input data types and ranges before calculation
- Handle empty DataFrames and missing values explicitly
- Use typed output structures — not raw dicts or tuples

## Error Handling

```python
# CORRECT
try:
    result = calculate(inputs)
except Exception as exc:
    logger.warning("Calculation failed", extra={"error": str(exc)})
    raise RuntimeError("Calculation failed. Check input values.") from exc
```

## Secret Management

```python
# CORRECT
api_key = os.environ.get("EMISSIONS_API_KEY")
if not api_key:
    raise RuntimeError("EMISSIONS_API_KEY must be set")
```

## Test Requirements

- Every calculation function has at least one positive-case and one edge-case test
- Run: `pytest tests -q`
