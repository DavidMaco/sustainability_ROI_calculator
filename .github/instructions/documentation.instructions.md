---
applyTo: "**"
---

# Documentation Standards — Sustainability ROI Calculator

## When to Write Documentation

Write or update documentation when:

- Adding a new pipeline stage or ROI calculation method
- Changing output file formats or column schemas
- Modifying environment variable requirements

Do **not** add docstrings or comments to code you did not change.

## Docstring Format (Python)

```python
def calculate_roi(baseline: float, investment: float, annual_savings: float) -> float:
    """Calculate return on investment for a sustainability initiative.

    Args:
        baseline: Current annual cost before investment.
        investment: One-time investment amount.
        annual_savings: Annual savings resulting from the investment.

    Returns:
        ROI as a percentage (0-100+).

    Raises:
        ValueError: If investment is zero or negative.
    """
```

## README Updates

Every `README.md` must include:

1. One-sentence product description
2. Quickstart commands
3. Environment variable list

## Changelog

Format: `## [YYYY-MM-DD] — description`.

## Standards Docs Location

Implementation status lives in `docs/`:

- `STANDARDS_IMPLEMENTATION.md`
- `SKILLS_IMPLEMENTATION.md`
- `ROLLOUT_IMPLEMENTATION.md`
