"""Streamlit entry point — works both locally (python run_ui.py) and on Community Cloud."""
import sys
from pathlib import Path

_root = Path(__file__).parent.resolve()
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

_app = _root / "src" / "ui" / "app.py"

# On Community Cloud, Streamlit runs this file directly — exec app.py in-process.
# Locally, subprocess launch is fine too, but exec works everywhere.
exec(compile(_app.read_text(), str(_app), "exec"), {"__file__": str(_app), "__name__": "__main__"})
