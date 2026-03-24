---
applyTo: "**"
---

# Output Quality — Sustainability ROI Calculator

Standards for data outputs, generated reports, and any UI components.

## Data Output Standards

- All CSV outputs must have consistent column names documented in README
- JSON outputs must conform to the schema defined in `docs/`
- Report files must be human-readable without requiring technical context

## Streamlit Standards (if applicable)

- One `st.set_page_config()` per app entry point only
- Use `@st.cache_data` for data-loading functions
- No secrets in source; use `st.secrets` or env vars
- Handle empty DataFrames gracefully in all UI components

## Shared Rules

- No hardcoded file paths — use config or relative paths from project root
- No commented-out code in committed files
