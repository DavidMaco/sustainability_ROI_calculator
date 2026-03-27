"""
Sustainability ROI Calculator — Secrets Adapter

Provides a uniform ``get_secret(key)`` interface that resolves secrets from
the configured backend, with transparent fallback to plain environment variables.

Backend selection via ``SUST_SECRETS_BACKEND`` (default: ``env``):

  env   — Plain ``os.environ`` lookup (no extra dependencies)
  vault — HashiCorp Vault KV v2 (requires ``pip install hvac``)
  aws   — AWS Secrets Manager JSON secret (requires ``pip install boto3``)
  gcp   — GCP Secret Manager (requires ``pip install google-cloud-secret-manager``)

Configuration environment variables per backend:

  Vault:
    SUST_VAULT_ADDR          Vault server URL, e.g. https://vault.example.com
    SUST_VAULT_MOUNT          KV mount path (default: secret)
    SUST_VAULT_PATH           Secret path inside the mount (default: sustainability-roi)
    SUST_VAULT_TOKEN          Static token (preferred for dev/CI)
    SUST_VAULT_ROLE_ID        AppRole role_id (production preferred over token)
    SUST_VAULT_SECRET_ID      AppRole secret_id

  AWS:
    SUST_AWS_SECRETS_REGION   AWS region, e.g. eu-west-1
    SUST_AWS_SECRET_NAME      Secret name in Secrets Manager (default: sustainability-roi)
    Standard AWS SDK env vars (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, etc.)

  GCP:
    SUST_GCP_PROJECT_ID       GCP project ID
    SUST_GCP_SECRET_NAME      Override the secret ID (default: sustainability-roi-<KEY_lower>)
    SUST_GCP_SECRET_VERSION   Version to access (default: latest)
    GOOGLE_APPLICATION_CREDENTIALS or Workload Identity for authentication

Usage::

    from secrets_adapter import get_secret, require_secret

    db_pass = require_secret("DB_PASSWORD")           # raises if absent
    api_key = get_secret("EXTERNAL_API_KEY", default="")  # returns "" if absent
"""

import json
import logging
import os
from functools import lru_cache

logger = logging.getLogger("sustainability_roi.secrets")

_BACKEND: str = os.getenv("SUST_SECRETS_BACKEND", "env").lower()
_VALID_BACKENDS = frozenset({"env", "vault", "aws", "gcp"})


# ─── Backend implementations ─────────────────────────────────────────


def _vault_get(key: str) -> str | None:
    """Resolve a secret from HashiCorp Vault KV v2."""
    try:
        import hvac  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError("hvac is required for the Vault backend. " "Install it with: pip install hvac") from exc

    addr = os.environ.get("SUST_VAULT_ADDR")
    if not addr:
        raise RuntimeError("SUST_VAULT_ADDR must be set when using the Vault backend")

    mount = os.getenv("SUST_VAULT_MOUNT", "secret")
    path = os.getenv("SUST_VAULT_PATH", "sustainability-roi")
    token = os.getenv("SUST_VAULT_TOKEN")
    role_id = os.getenv("SUST_VAULT_ROLE_ID")
    secret_id = os.getenv("SUST_VAULT_SECRET_ID")

    client = hvac.Client(url=addr)
    if token:
        client.token = token
    elif role_id and secret_id:
        client.auth.approle.login(role_id=role_id, secret_id=secret_id)
    else:
        raise RuntimeError(
            "Vault backend requires SUST_VAULT_TOKEN or " "both SUST_VAULT_ROLE_ID and SUST_VAULT_SECRET_ID"
        )

    if not client.is_authenticated():
        raise RuntimeError("Vault authentication failed — verify token or AppRole credentials")

    response = client.secrets.kv.v2.read_secret_version(
        mount_point=mount,
        path=path,
        raise_on_deleted_version=True,
    )
    payload: dict[str, str] = response["data"]["data"]
    return payload.get(key)


def _aws_get(key: str) -> str | None:
    """Resolve a secret from AWS Secrets Manager (JSON-encoded secret)."""
    try:
        import boto3  # type: ignore[import-untyped]
        from botocore.exceptions import ClientError  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError("boto3 is required for the AWS backend. " "Install it with: pip install boto3") from exc

    region = os.environ.get("SUST_AWS_SECRETS_REGION")
    if not region:
        raise RuntimeError("SUST_AWS_SECRETS_REGION must be set when using the AWS backend")

    secret_name = os.getenv("SUST_AWS_SECRET_NAME", "sustainability-roi")

    client = boto3.client("secretsmanager", region_name=region)
    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as exc:
        raise RuntimeError(f"AWS Secrets Manager could not retrieve {secret_name!r}: {exc}") from exc

    raw: str = response.get("SecretString") or ""
    try:
        data: dict[str, str] = json.loads(raw)
    except json.JSONDecodeError:
        # Single-value secret — return as-is only if the key matches the secret name
        return raw if key == secret_name else None

    return data.get(key)


def _gcp_get(key: str) -> str | None:
    """Resolve a secret from GCP Secret Manager."""
    try:
        from google.cloud import secretmanager  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError(
            "google-cloud-secret-manager is required for the GCP backend. "
            "Install it with: pip install google-cloud-secret-manager"
        ) from exc

    project_id = os.environ.get("SUST_GCP_PROJECT_ID")
    if not project_id:
        raise RuntimeError("SUST_GCP_PROJECT_ID must be set when using the GCP backend")

    secret_id = os.getenv("SUST_GCP_SECRET_NAME", f"sustainability-roi-{key.lower()}")
    version = os.getenv("SUST_GCP_SECRET_VERSION", "latest")
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"

    sm_client = secretmanager.SecretManagerServiceClient()
    try:
        resp = sm_client.access_secret_version(request={"name": name})
    except Exception as exc:
        raise RuntimeError(f"GCP Secret Manager could not retrieve {secret_id!r} v{version}: {exc}") from exc

    return resp.payload.data.decode("utf-8").strip()


def _env_get(key: str) -> str | None:
    return os.environ.get(key)


# ─── Internal cached resolver ─────────────────────────────────────────

_RESOLVERS = {
    "env": _env_get,
    "vault": _vault_get,
    "aws": _aws_get,
    "gcp": _gcp_get,
}


@lru_cache(maxsize=256)
def _resolve(key: str) -> str | None:
    """Internal cached lookup — resolves via the active backend then env fallback."""
    if _BACKEND not in _VALID_BACKENDS:
        raise ValueError(f"Unknown SUST_SECRETS_BACKEND={_BACKEND!r}. " f"Valid values: {sorted(_VALID_BACKENDS)}")

    resolver = _RESOLVERS[_BACKEND]
    value: str | None = None
    try:
        value = resolver(key)
    except Exception:
        logger.exception(
            "Secrets backend %r raised an error for key %r; " "falling back to environment variable",
            _BACKEND,
            key,
        )

    # Always try env var as an explicit fallback (except when backend is already env)
    if value is None and _BACKEND != "env":
        value = _env_get(key)

    return value


# ─── Public interface ─────────────────────────────────────────────────


def get_secret(key: str, *, default: str | None = None) -> str | None:
    """Return the secret value for *key*, or *default* if not found anywhere.

    Resolution order:
      1. Primary backend (Vault / AWS SM / GCP SM / env)
      2. Plain ``os.environ`` fallback (when primary backend ≠ env and returns nothing)
      3. *default* parameter

    Results are cached per key — call ``clear_secrets_cache()`` to invalidate.
    """
    value = _resolve(key)
    if value is None:
        value = default
    if value is not None:
        logger.debug("Resolved secret %r via backend %r", key, _BACKEND)
    else:
        logger.debug("Secret %r not found in any backend (returning default)", key)
    return value


def require_secret(key: str) -> str:
    """Like ``get_secret`` but raises ``RuntimeError`` if the key is missing.

    Use this for secrets that are mandatory at startup (e.g. DB credentials,
    encryption keys).  The error message guides the operator to the correct
    configuration env var.
    """
    value = get_secret(key)
    if value is None:
        raise RuntimeError(
            f"Required secret {key!r} is not set. "
            f"Configure it via SUST_SECRETS_BACKEND={_BACKEND!r} "
            f"or set the environment variable {key!r} directly."
        )
    return value


def clear_secrets_cache() -> None:
    """Invalidate the in-process secret cache (useful for tests and key rotation)."""
    _resolve.cache_clear()
    logger.debug("Secrets cache cleared")
