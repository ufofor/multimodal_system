"""Launch the Streamlit UI. Run: python run_ui.py"""
import subprocess
import sys

subprocess.run(
    [sys.executable, "-m", "streamlit", "run", "src/ui/app.py", "--server.headless=false"],
    check=True,
)
