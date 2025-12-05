"""
Tests for build process and executable creation.
"""

import pytest
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


class TestBuild:
    """Test build process."""
    
    def test_build_script_exists(self):
        """Test build.py exists and is valid."""
        build_script = ROOT / "build.py"
        assert build_script.exists(), "build.py not found"
        
        # Check syntax
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(build_script)],
            capture_output=True
        )
        assert result.returncode == 0, f"build.py syntax error: {result.stderr.decode()}"
    
    def test_main_py_exists(self):
        """Test main.py exists and is valid."""
        main_script = ROOT / "main.py"
        assert main_script.exists(), "main.py not found"
        
        # Check syntax
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(main_script)],
            capture_output=True
        )
        assert result.returncode == 0, f"main.py syntax error: {result.stderr.decode()}"
    
    def test_core_structure(self):
        """Test core directory structure."""
        core_dir = ROOT / "core"
        assert core_dir.exists(), "core/ directory not found"
        
        required_files = [
            "models.py",
            "services.py",
            "interfaces.py",
            "controller.py",
            "drivers/__init__.py",
            "drivers/device_factory.py",
            "drivers/elk_bledom.py"
        ]
        
        for file_path in required_files:
            full_path = core_dir / file_path
            assert full_path.exists(), f"Required file not found: {file_path}"
    
    def test_ui_structure(self):
        """Test UI directory structure."""
        ui_dir = ROOT / "ui"
        assert ui_dir.exists(), "ui/ directory not found"
        
        required_files = [
            "main_window.py",
            "components.py",
            "viewmodels.py"
        ]
        
        for file_path in required_files:
            full_path = ui_dir / file_path
            assert full_path.exists(), f"Required file not found: {file_path}"

