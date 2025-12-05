"""
Test executable after build.
Checks if EXE exists and can be analyzed.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
EXE_PATH = ROOT / "dist" / "Commander.exe"


def test_exe_exists():
    """Test that EXE file exists."""
    if EXE_PATH.exists():
        size_mb = EXE_PATH.stat().st_size / (1024 * 1024)
        print(f"✅ EXE found: {EXE_PATH}")
        print(f"   Size: {size_mb:.2f} MB")
        return True
    else:
        print(f"❌ EXE not found: {EXE_PATH}")
        return False


def test_exe_structure():
    """Test EXE file structure."""
    if not EXE_PATH.exists():
        return False
    
    # Check if it's a valid PE file (Windows executable)
    try:
        with open(EXE_PATH, 'rb') as f:
            header = f.read(2)
            if header == b'MZ':  # PE file signature
                print("✅ EXE has valid PE header")
                return True
            else:
                print("❌ EXE has invalid header")
                return False
    except Exception as e:
        print(f"❌ Error reading EXE: {e}")
        return False


def test_dependencies():
    """Test that required dependencies are in requirements.txt."""
    req_file = ROOT / "requirements.txt"
    if not req_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    required = ["customtkinter", "bleak", "psutil"]
    found = []
    
    with open(req_file, 'r') as f:
        content = f.read().lower()
        for dep in required:
            if dep.lower() in content:
                found.append(dep)
                print(f"  ✓ {dep} in requirements.txt")
            else:
                print(f"  ✗ {dep} NOT in requirements.txt")
    
    if len(found) == len(required):
        print("✅ All dependencies in requirements.txt")
        return True
    else:
        print(f"❌ Missing dependencies: {set(required) - set(found)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing built executable...")
    print("=" * 60)
    
    exists = test_exe_exists()
    structure = test_exe_structure() if exists else False
    
    print("\n" + "=" * 60)
    print("Testing dependencies...")
    print("=" * 60)
    deps = test_dependencies()
    
    print("\n" + "=" * 60)
    if exists and structure:
        print("✅ EXE build verification PASSED!")
        print(f"\nExecutable: {EXE_PATH}")
        print("\nNote: To test EXE execution, run it manually:")
        print(f"  {EXE_PATH}")
    else:
        print("❌ EXE build verification FAILED!")
        if not exists:
            print("  - EXE file not found. Run build.py first.")
        if not structure:
            print("  - EXE file structure invalid.")

