# Production Readiness — Sustainability ROI Calculator v2.0.2

## Status: Pilot-Ready

### Ready
- [x] Modular package architecture (domain / ingestion / pipeline / pages)
- [x] Typed data contracts (Pydantic models)
- [x] Centralised, env-driven configuration with production guard
- [x] Extensible ingestion layer (CSV adapter, pluggable)
- [x] Unit + integration test suite (21 tests, pytest)
- [x] CI/CD pipeline (lint + format + smoke test + pytest)
- [x] Streamlit multi-page UI
- [x] Deterministic reproducibility (seeded generation)
- [x] JSON-safe serialisation (no Python dict strings in CSV)
- [x] Structured logging
- [x] Correct unit conversions (kg→ton, liters→kL) across all formulas
- [x] Input validation with clear error messages for unknown materials
- [x] Unicode-safe console output on Windows terminals
- [x] MIT License

### Remaining for Full Production
- [ ] Authentication / RBAC on Streamlit
- [ ] Secrets management (Streamlit Cloud secrets or vault)
- [ ] Observability (structured log aggregation, health endpoint)
- [ ] Backup / versioning of output artifacts
- [ ] Load testing for Streamlit under concurrent users
- [ ] External data connector (API / DB adapter)
- [ ] NPV / multi-year discounted analysis
- [ ] Docker containerisation
