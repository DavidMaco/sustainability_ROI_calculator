"""Artifact backup/versioning helpers for pipeline outputs."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def create_artifact_backup(data_dir: Path, *, retention: int = 20) -> tuple[Path, Path] | None:
    """Create a timestamped zip backup and JSON manifest for current artifacts.

    Returns:
        (zip_path, manifest_path) if artifacts exist; otherwise None.
    """
    expected = [
        "sustainability_materials_comparison.csv",
        "company_scenarios.csv",
        "sustainability_roi_analysis.csv",
        "sustainability_summary.json",
        "sustainability_calculator_template.csv",
    ]

    artifacts = [data_dir / name for name in expected if (data_dir / name).exists()]
    if not artifacts:
        return None

    backup_dir = data_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    zip_path = backup_dir / f"artifacts_{stamp}.zip"
    manifest_path = backup_dir / f"artifacts_{stamp}.manifest.json"

    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for path in artifacts:
            zf.write(path, arcname=path.name)

    manifest = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "zip_file": zip_path.name,
        "files": [
            {"name": p.name, "bytes": p.stat().st_size, "sha256": _sha256(p)}
            for p in sorted(artifacts, key=lambda x: x.name)
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    _prune_old_backups(backup_dir, retention)
    return zip_path, manifest_path


def _prune_old_backups(backup_dir: Path, retention: int) -> None:
    zips = sorted(backup_dir.glob("artifacts_*.zip"))
    manifests = sorted(backup_dir.glob("artifacts_*.manifest.json"))
    excess = max(0, len(zips) - retention)
    if excess <= 0:
        return
    for stale in zips[:excess]:
        stale.unlink(missing_ok=True)
    for stale in manifests[:excess]:
        stale.unlink(missing_ok=True)
