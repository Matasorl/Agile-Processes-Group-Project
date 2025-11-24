import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "Database/Scripts/rating_runtime_correlation.py",
    "Database/Scripts/Stars-Director-Rating-Visualisation.py",
    "Database/Scripts/avg_rating_per_runtime.py",
    "Database/Scripts/genre_analytics_dashboard.py",
    "Database/Scripts/Genre_Avg_Rating_DB.py",

]


def test_scripts_execute_cleanly():
    for script in SCRIPTS:
        path = Path(script)
        assert path.exists(), f"Missing script: {script}"

        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, (
            f"\n Script failed: {script}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
