"""
Tests for verifying project structure and imports after reorganization.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


class TestStructure:
    """Test project structure and imports."""
    
    def test_core_models_import(self):
        """Test core.models imports."""
        from core.models import (
            Color, ColorMode, TransitionStyle,
            DeviceConfig, AppPreferences, DeviceStatus, ColorPreset
        )
        assert Color is not None
        assert ColorMode is not None
        assert DeviceConfig is not None
    
    def test_core_services_import(self):
        """Test core.services imports."""
        from core.services import ConfigService, LoggerService
        assert ConfigService is not None
        assert LoggerService is not None
    
    def test_core_interfaces_import(self):
        """Test core.interfaces imports."""
        from core.interfaces import AbstractLedDevice
        assert AbstractLedDevice is not None
    
    def test_core_controller_import(self):
        """Test core.controller imports."""
        from core.controller import BleDeviceController, BleApplicationBridge
        assert BleDeviceController is not None
        assert BleApplicationBridge is not None
    
    def test_core_drivers_import(self):
        """Test core.drivers imports."""
        from core.drivers.device_factory import DeviceFactory
        from core.drivers.elk_bledom import ElkBledomDriver
        from core.drivers.triones import TrionesDriver
        from core.drivers.magichome import MagicHomeDriver
        from core.drivers.tuya import TuyaDriver
        
        assert DeviceFactory is not None
        assert ElkBledomDriver is not None
        assert TrionesDriver is not None
        assert MagicHomeDriver is not None
        assert TuyaDriver is not None
    
    def test_ui_imports(self):
        """Test UI imports."""
        from ui.main_window import DashboardView
        from ui.viewmodels import Application
        from ui.components import ColorWheelPicker, NavButton
        
        assert DashboardView is not None
        assert Application is not None
    
    def test_main_imports(self):
        """Test main.py can be imported."""
        import main
        assert main is not None
        assert hasattr(main, 'main')
    
    def test_driver_factory_works(self):
        """Test DeviceFactory can create drivers."""
        from core.drivers.device_factory import DeviceFactory
        
        # Test explicit protocol
        driver = DeviceFactory.create_driver(protocol_type="elk_bledom")
        assert driver is not None
        assert driver.get_protocol_name() == "ELK-BLEDOM"
        
        # Test available protocols
        protocols = DeviceFactory.get_available_protocols()
        assert "elk_bledom" in protocols
        assert "triones" in protocols
        assert "magichome" in protocols
        assert "tuya" in protocols
    
    def test_models_functionality(self):
        """Test core models work correctly."""
        from core.models import Color, ColorMode
        
        # Test Color
        color = Color(255, 128, 64)
        assert color.r == 255
        assert color.g == 128
        assert color.b == 64
        assert color.to_hex() == "#FF8040"
        
        # Test ColorMode
        assert ColorMode.MANUAL.value == "MANUAL"
        assert ColorMode.CPU.value == "CPU"
    
    def test_config_service_works(self):
        """Test ConfigService works."""
        from core.services import ConfigService
        from core.models import DeviceConfig, AppPreferences
        
        config = ConfigService.get_device_config()
        assert isinstance(config, DeviceConfig)
        assert config.target_mac is not None
        
        prefs = ConfigService.get_preferences()
        assert isinstance(prefs, AppPreferences)
        assert 0.0 <= prefs.brightness <= 1.0

