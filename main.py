"""
Uvicorn entrypoint from repo root.

Run from `distributed-task-system/`:
  uvicorn main:app --host 0.0.0.0 --port 8000

To run from `gateway/` instead:
  cd gateway
  uvicorn main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_GATEWAY_DIR = Path(__file__).resolve().parent / "gateway"

if not (_GATEWAY_DIR / "main.py").is_file():
    raise RuntimeError(f"Expected gateway app at {_GATEWAY_DIR / 'main.py'}")

if str(_GATEWAY_DIR) not in sys.path:
    sys.path.insert(0, str(_GATEWAY_DIR))

_spec = importlib.util.spec_from_file_location("_gateway_main", _GATEWAY_DIR / "main.py")
if _spec is None or _spec.loader is None:
    raise RuntimeError("Cannot load gateway/main.py")

_mod = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("_gateway_main", _mod)
_spec.loader.exec_module(_mod)
app = _mod.app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
