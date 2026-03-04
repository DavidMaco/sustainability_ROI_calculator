"""Root conftest — ensure project root is on sys.path for all tests."""

import sys
from pathlib import Path

# Add project root so `import config`, `import domain.*`, etc. resolve cleanly
_PROJECT_ROOT = str(Path(__file__).resolve().parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
