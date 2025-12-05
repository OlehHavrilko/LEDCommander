"""
Test project structure without importing dependencies.
"""

from pathlib import Path

ROOT = Path(__file__).parent

def test_structure():
    """Test that all required files exist."""
    errors = []
    
    # Core files
    core_files = [
        "core/__init__.py",
        "core/models.py",
        "core/services.py",
        "core/interfaces.py",
        "core/controller.py",
        "core/drivers/__init__.py",
        "core/drivers/device_factory.py",
        "core/drivers/elk_bledom.py",
        "core/drivers/triones.py",
        "core/drivers/magichome.py",
        "core/drivers/tuya.py",
    ]
    
    print("Checking core files...")
    for file_path in core_files:
        full_path = ROOT / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            errors.append(f"Missing: {file_path}")
            print(f"  ✗ {file_path} - NOT FOUND")
    
    # UI files
    ui_files = [
        "ui/__init__.py",
        "ui/main_window.py",
        "ui/components.py",
        "ui/viewmodels.py",
    ]
    
    print("\nChecking UI files...")
    for file_path in ui_files:
        full_path = ROOT / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            errors.append(f"Missing: {file_path}")
            print(f"  ✗ {file_path} - NOT FOUND")
    
    # Root files
    root_files = [
        "main.py",
        "build.py",
        "requirements.txt",
    ]
    
    print("\nChecking root files...")
    for file_path in root_files:
        full_path = ROOT / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            errors.append(f"Missing: {file_path}")
            print(f"  ✗ {file_path} - NOT FOUND")
    
    return errors


def test_syntax():
    """Test Python syntax of key files."""
    import py_compile
    import sys
    
    errors = []
    files_to_check = [
        "core/models.py",
        "core/services.py",
        "core/interfaces.py",
        "core/controller.py",
        "ui/main_window.py",
        "ui/viewmodels.py",
        "main.py",
        "build.py",
    ]
    
    print("\nChecking Python syntax...")
    for file_path in files_to_check:
        full_path = ROOT / file_path
        if not full_path.exists():
            continue
        
        try:
            py_compile.compile(str(full_path), doraise=True)
            print(f"  ✓ {file_path}")
        except py_compile.PyCompileError as e:
            errors.append(f"Syntax error in {file_path}: {e}")
            print(f"  ✗ {file_path} - SYNTAX ERROR: {e}")
        except Exception as e:
            errors.append(f"Error checking {file_path}: {e}")
            print(f"  ✗ {file_path} - ERROR: {e}")
    
    return errors


if __name__ == "__main__":
    print("=" * 60)
    print("Testing project structure...")
    print("=" * 60)
    
    structure_errors = test_structure()
    syntax_errors = test_syntax()
    
    print("\n" + "=" * 60)
    if not structure_errors and not syntax_errors:
        print("✅ Structure check PASSED!")
        print("\nNote: Import tests require dependencies (bleak, customtkinter, psutil)")
        print("Run 'pip install -r requirements.txt' to install dependencies")
    else:
        print("❌ Structure check FAILED!")
        if structure_errors:
            print(f"\nMissing files ({len(structure_errors)}):")
            for err in structure_errors:
                print(f"  - {err}")
        if syntax_errors:
            print(f"\nSyntax errors ({len(syntax_errors)}):")
            for err in syntax_errors:
                print(f"  - {err}")

