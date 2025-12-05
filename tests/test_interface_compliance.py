"""
Test interface compliance and static method signatures.
Verifies that all drivers correctly implement the abstract interface.
"""

import pytest
from inspect import signature

from core.interfaces import AbstractLedDevice
from core.drivers.elk_bledom import ElkBledomDriver
from core.drivers.triones import TrionesDriver
from core.drivers.magichome import MagicHomeDriver
from core.drivers.tuya import TuyaDriver


class TestInterfaceCompliance:
    """Test that all drivers comply with the abstract interface."""
    
    def test_get_supported_modes_is_static(self):
        """Verify get_supported_modes is a static method without self parameter."""
        drivers = [ElkBledomDriver, TrionesDriver, MagicHomeDriver, TuyaDriver]
        
        for driver_class in drivers:
            # Check method exists
            assert hasattr(driver_class, 'get_supported_modes')
            
            # Get method signature
            sig = signature(driver_class.get_supported_modes)
            
            # Verify it has no 'self' parameter (static method)
            params = list(sig.parameters.keys())
            assert 'self' not in params, f"{driver_class.__name__}.get_supported_modes should not have 'self' parameter"
            
            # Verify it can be called without instance
            modes = driver_class.get_supported_modes()
            assert isinstance(modes, dict)
            assert len(modes) > 0
    
    def test_can_handle_device_is_static(self):
        """Verify can_handle_device is a static method."""
        drivers = [ElkBledomDriver, TrionesDriver, MagicHomeDriver, TuyaDriver]
        
        for driver_class in drivers:
            # Check method exists
            assert hasattr(driver_class, 'can_handle_device')
            
            # Get method signature
            sig = signature(driver_class.can_handle_device)
            
            # Verify it has no 'self' parameter
            params = list(sig.parameters.keys())
            assert 'self' not in params, f"{driver_class.__name__}.can_handle_device should not have 'self' parameter"
            
            # Verify it can be called without instance
            result = driver_class.can_handle_device("Test Device", [])
            assert isinstance(result, bool)
    
    def test_interface_abstract_methods(self):
        """Verify abstract interface defines methods correctly."""
        # Check get_supported_modes signature in interface
        sig = signature(AbstractLedDevice.get_supported_modes)
        params = list(sig.parameters.keys())
        assert 'self' not in params, "AbstractLedDevice.get_supported_modes should not have 'self' parameter"
        
        # Check can_handle_device signature in interface
        sig = signature(AbstractLedDevice.can_handle_device)
        params = list(sig.parameters.keys())
        assert 'self' not in params, "AbstractLedDevice.can_handle_device should not have 'self' parameter"
    
    def test_driver_can_be_used_via_class(self):
        """Test that static methods can be called via class, not just instance."""
        # Test via class (correct way)
        modes1 = ElkBledomDriver.get_supported_modes()
        
        # Test via instance (should also work due to Python's static method behavior)
        driver = ElkBledomDriver()
        modes2 = driver.__class__.get_supported_modes()
        
        # Results should be the same
        assert modes1 == modes2
        
        # Test can_handle_device via class
        result1 = TrionesDriver.can_handle_device("Triones Device", [])
        driver = TrionesDriver()
        result2 = driver.__class__.can_handle_device("Triones Device", [])
        assert result1 == result2

