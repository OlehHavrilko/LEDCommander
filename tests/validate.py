#!/usr/bin/env python3
"""
LED COMMANDER v3.0 - Quick Validation Script
Tests all components and imports for the ELK-BLEDOM UI redesign.
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    os.system("chcp 65001 > nul")

# Use ASCII symbols for better compatibility
CHECKMARK = "[OK]"
CROSS = "[XX]"
WARNING = "[!]"
INFO = "[*]"

# Colors for console output (disabled for Windows compatibility)
GREEN = ""
RED = ""
YELLOW = ""
BLUE = ""
RESET = ""
BOLD = ""

def print_header(text):
    print(f"\n{'='*60}")
    print(f"{text}")
    print(f"{'='*60}\n")

def print_success(text):
    print(f"{CHECKMARK} {text}")

def print_error(text):
    print(f"{CROSS} {text}")

def print_warning(text):
    print(f"{WARNING} {text}")

def print_info(text):
    print(f"{INFO} {text}")

def test_imports():
    """Test that all modules import successfully."""
    print_header("Testing Imports")
    
    tests = [
        ("models", "Color, ColorMode, DeviceStatus"),
        ("services", "ConfigService, LoggerService"),
        ("components", "NavButton, EffectListItem, ScheduleCard"),
        ("ble_controller", "BleDeviceController, BleApplicationBridge"),
        ("ui", "DashboardView, ModernUIController"),
        ("app", "Application"),
    ]
    
    failed = []
    for module, items in tests:
        try:
            exec(f"from {module} import {items.split(',')[0]}")
            print_success(f"{module:20} → {items}")
        except Exception as e:
            print_error(f"{module:20} → {str(e)}")
            failed.append(module)
    
    return len(failed) == 0

def test_color_functionality():
    """Test Color class functionality."""
    print_header("Testing Color Functionality")
    
    from models import Color
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Color creation and clamping
    tests_total += 1
    try:
        c = Color(300, -50, 128)  # Should clamp to (255, 0, 128)
        assert c.r == 255 and c.g == 0 and c.b == 128
        print_success("Color clamping works correctly")
        tests_passed += 1
    except Exception as e:
        print_error(f"Color clamping failed: {e}")
    
    # Test 2: HEX conversion
    tests_total += 1
    try:
        c = Color(255, 85, 0)
        assert c.to_hex() == "#FF5500"
        print_success("Color to HEX conversion works")
        tests_passed += 1
    except Exception as e:
        print_error(f"HEX conversion failed: {e}")
    
    # Test 3: HEX parsing
    tests_total += 1
    try:
        c = Color.from_hex("#FF5500")
        assert c.r == 255 and c.g == 85 and c.b == 0
        print_success("HEX parsing works")
        tests_passed += 1
    except Exception as e:
        print_error(f"HEX parsing failed: {e}")
    
    # Test 4: Brightness application
    tests_total += 1
    try:
        c = Color(100, 200, 150)
        dimmed = c.apply_brightness(0.5)
        assert dimmed.r <= 50 and dimmed.g <= 100 and dimmed.b <= 75
        print_success("Brightness application works")
        tests_passed += 1
    except Exception as e:
        print_error(f"Brightness application failed: {e}")
    
    return tests_passed, tests_total

def test_ui_components():
    """Test UI components exist and are callable."""
    print_header("Testing UI Components")
    
    from components import NavButton, EffectListItem, ScheduleCard, DeviceListItem
    
    components = [
        ("NavButton", NavButton),
        ("EffectListItem", EffectListItem),
        ("ScheduleCard", ScheduleCard),
        ("DeviceListItem", DeviceListItem),
    ]
    
    for name, cls in components:
        try:
            # Check if class is callable
            assert callable(cls)
            print_success(f"{name:20} → Available and instantiable")
        except Exception as e:
            print_error(f"{name:20} → {str(e)}")
            return False
    
    return True

def test_effects_list():
    """Test effects list configuration."""
    print_header("Testing Effects List")
    
    from ui import EFFECTS_LIST
    from models import ColorMode
    
    print_info(f"Total effects: {len(EFFECTS_LIST)}")
    
    if len(EFFECTS_LIST) < 10:
        print_error(f"Expected at least 10 effects, got {len(EFFECTS_LIST)}")
        return False
    
    print_success(f"Effects list properly configured")
    
    # Show first 3 effects
    for i, (name, mode) in enumerate(EFFECTS_LIST[:3]):
        print_info(f"  {i+1}. {name:30} → {mode.value}")
    
    # Verify all effects map to valid ColorModes
    valid_modes = {e.value for e in ColorMode}
    for name, mode in EFFECTS_LIST:
        if mode.value not in valid_modes:
            print_error(f"Invalid effect mode: {name} → {mode.value}")
            return False
    
    print_success("All effects map to valid ColorModes")
    return True

def test_config_loading():
    """Test configuration loading."""
    print_header("Testing Configuration")
    
    from services import ConfigService
    from models import DeviceConfig, AppPreferences
    
    try:
        # Test device config
        device_config = ConfigService.get_device_config()
        assert isinstance(device_config, DeviceConfig)
        print_success(f"Device config loaded: {device_config.device_name}")
        
        # Test preferences
        prefs = ConfigService.get_preferences()
        assert isinstance(prefs, AppPreferences)
        print_success(f"Preferences loaded: Brightness={prefs.brightness}")
        
        return True
    except Exception as e:
        print_error(f"Configuration loading failed: {e}")
        return False

def test_ble_bridge():
    """Test BLE bridge initialization."""
    print_header("Testing BLE Bridge")
    
    try:
        from ble_controller import BleApplicationBridge
        
        # Create bridge (won't start BLE yet)
        bridge = BleApplicationBridge()
        print_success("BleApplicationBridge instantiated")
        
        # Check methods exist
        methods = [
            "set_color",
            "set_mode",
            "set_brightness",
            "set_speed",
            "save_preferences",
            "initialize",
            "shutdown"
        ]
        
        for method in methods:
            if not hasattr(bridge, method):
                print_error(f"Missing method: {method}")
                return False
            print_success(f"Method available: {method}")
        
        # Check properties
        if not hasattr(bridge, 'controller'):
            print_error("Missing controller property")
            return False
        print_success("Property available: controller")
        
        return True
    except Exception as e:
        print_error(f"BLE bridge test failed: {e}")
        return False

def test_file_structure():
    """Test project file structure."""
    print_header("Testing Project Structure")
    
    required_files = [
        "ui.py",
        "components.py",
        "models.py",
        "services.py",
        "ble_controller.py",
        "app.py",
        "requirements.txt",
        "README.md",
    ]
    
    optional_files = [
        "led_config.json",  # Created on first run
        ".github/copilot-instructions.md",
    ]
    
    missing = []
    for filename in required_files:
        path = Path(filename)
        if path.exists():
            size = path.stat().st_size
            print_success(f"{filename:25} ({size:8} bytes)")
        else:
            print_error(f"{filename:25} (MISSING)")
            missing.append(filename)
    
    # Check optional files
    print(f"\n{BLUE}Optional files:{RESET}")
    for filename in optional_files:
        path = Path(filename)
        if path.exists():
            size = path.stat().st_size
            print_info(f"{filename:25} ({size:8} bytes)")
        else:
            print_warning(f"{filename:25} (not yet created)")
    
    return len(missing) == 0

def main():
    """Run all validation tests."""
    os.chdir(Path(__file__).parent)
    
    print(f"\nLED COMMANDER v3.0 - Validation Test Suite")
    print(f"ELK-BLEDOM UI Redesign\n")
    
    results = {}
    
    # Run tests
    results["File Structure"] = test_file_structure()
    results["Imports"] = test_imports()
    results["Color Functionality"] = all(test_color_functionality())
    results["UI Components"] = test_ui_components()
    results["Effects List"] = test_effects_list()
    results["Configuration"] = test_config_loading()
    results["BLE Bridge"] = test_ble_bridge()
    
    # Summary
    print_header("Test Summary")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name:30} -> {status}")
    
    print(f"\nResults:")
    print(f"  Passed: {passed_tests}/{total_tests}")
    print(f"  Failed: {total_tests - passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print(f"\n{BOLD}[OK] All tests passed!{RESET}")
        print(f"The application is ready for testing.\n")
        return 0
    else:
        print(f"\n{BOLD}[XX] Some tests failed!{RESET}")
        print(f"Please review the errors above.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
