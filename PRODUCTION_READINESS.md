# Production Readiness - Sustainability ROI Calculator v2.0.2

## Status: Pilot-Ready

### Ready

- [x] Modular package architecture (domain / ingestion / pipeline / pages)
- [x] Typed data contracts (Pydantic models)
- [x] Centralised, env-driven configuration with production guard
- [x] Extensible ingestion layer (CSV adapter, pluggable)
- [x] Unit + integration test suite (21 tests, pytest)
- [x] CI/CD pipeline (lint + format + smoke test + pytest + scoped pyright gate)
- [x] Streamlit multi-page UI
- [x] Deterministic reproducibility (seeded generation)
- [x] JSON-safe serialisation (no Python dict strings in CSV)
- [x] Structured logging
- [x] Correct unit conversions (kg→ton, liters→kL) across all formulas
- [x] Input validation with clear error messages for unknown materials
- [x] Unicode-safe console output on Windows terminals
- [x] MIT License
- [x] Dockerfile and docker-compose deployment baseline
- [x] Authentication and RBAC guardrails for Streamlit pages
- [x] Session timeout controls for authenticated sessions
- [x] Artifact backup + checksum manifest versioning (`data/backups/`)
- [x] Health check script for app + artifact readiness
- [x] CI runtime gates for health endpoint and lightweight load probe
- [x] Managed auth secret file support (`SUST_AUTH_USERS_FILE`)
- [x] Prometheus-style `/metrics` and `/healthz` observability endpoint
- [x] Kubernetes manifest baseline (namespace, deployment, service, PVC, HPA, ingress)
- [x] Kubernetes Kustomize overlays for staging and production
- [x] Centralized log shipping baseline via Fluent Bit sidecar config
- [x] Kubernetes policy hardening baseline (service account, security context, network policies)
- [x] CI manifest validation for base and overlays (`kubectl kustomize` + dry-run apply)

### Remaining for Full Production

- [x] Secrets management (Vault / AWS SM / GCP SM adapter with env fallback)
- [x] Production log sink integration and dashboards (Loki via Fluent Bit in production overlay)
- [ ] Load testing for Streamlit under concurrent users
- [ ] External data connector (API / DB adapter)
- [ ] NPV / multi-year discounted analysis
- [ ] Expanded performance thresholds and trend dashboards in CI/CD
- [ ] Policy admission enforcement (OPA Gatekeeper/Kyverno) and signed image policies
