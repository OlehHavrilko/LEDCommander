"""
Test runner script for all driver tests.
Run with: python tests/run_tests.py
"""

import sys
import subprocess

if __name__ == "__main__":
    # Run pytest with verbose output
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd="."
    )
    sys.exit(result.returncode)

