"""
Simple import test to verify structure before building.
"""

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

def test_imports():
    """Test all critical imports."""
    errors = []
    
    try:
        from core.models import Color, ColorMode, DeviceConfig, AppPreferences
        print("✓ core.models imported")
    except Exception as e:
        errors.append(f"core.models: {e}")
        print(f"✗ core.models failed: {e}")
    
    try:
        from core.services import ConfigService, LoggerService
        print("✓ core.services imported")
    except Exception as e:
        errors.append(f"core.services: {e}")
        print(f"✗ core.services failed: {e}")
    
    try:
        from core.interfaces import AbstractLedDevice
        print("✓ core.interfaces imported")
    except Exception as e:
        errors.append(f"core.interfaces: {e}")
        print(f"✗ core.interfaces failed: {e}")
    
    try:
        from core.controller import BleDeviceController, BleApplicationBridge
        print("✓ core.controller imported")
    except Exception as e:
        errors.append(f"core.controller: {e}")
        print(f"✗ core.controller failed: {e}")
    
    try:
        from core.drivers.device_factory import DeviceFactory
        from core.drivers.elk_bledom import ElkBledomDriver
        print("✓ core.drivers imported")
    except Exception as e:
        errors.append(f"core.drivers: {e}")
        print(f"✗ core.drivers failed: {e}")
    
    try:
        from ui.main_window import DashboardView
        from ui.viewmodels import Application
        print("✓ ui modules imported")
    except Exception as e:
        errors.append(f"ui: {e}")
        print(f"✗ ui modules failed: {e}")
    
    try:
        import main
        print("✓ main.py imported")
    except Exception as e:
        errors.append(f"main: {e}")
        print(f"✗ main.py failed: {e}")
    
    if errors:
        print(f"\n❌ {len(errors)} import errors found:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("\n✅ All imports successful!")
        return True


def test_functionality():
    """Test basic functionality."""
    errors = []
    
    try:
        from core.models import Color
        color = Color(255, 128, 64)
        assert color.to_hex() == "#FF8040"
        print("✓ Color model works")
    except Exception as e:
        errors.append(f"Color model: {e}")
        print(f"✗ Color model failed: {e}")
    
    try:
        from core.drivers.device_factory import DeviceFactory
        driver = DeviceFactory.create_driver(protocol_type="elk_bledom")
        assert driver.get_protocol_name() == "ELK-BLEDOM"
        print("✓ DeviceFactory works")
    except Exception as e:
        errors.append(f"DeviceFactory: {e}")
        print(f"✗ DeviceFactory failed: {e}")
    
    try:
        from core.services import ConfigService
        config = ConfigService.get_device_config()
        assert config is not None
        print("✓ ConfigService works")
    except Exception as e:
        errors.append(f"ConfigService: {e}")
        print(f"✗ ConfigService failed: {e}")
    
    if errors:
        print(f"\n❌ {len(errors)} functionality errors found:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("\n✅ All functionality tests passed!")
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("Testing project structure and imports...")
    print("=" * 60)
    
    imports_ok = test_imports()
    print("\n" + "=" * 60)
    print("Testing functionality...")
    print("=" * 60)
    
    func_ok = test_functionality()
    
    print("\n" + "=" * 60)
    if imports_ok and func_ok:
        print("✅ ALL TESTS PASSED - Ready for build!")
        sys.exit(0)
    else:
        print("❌ TESTS FAILED - Fix errors before building!")
        sys.exit(1)

