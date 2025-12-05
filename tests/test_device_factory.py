"""
Unit tests for DeviceFactory.
Tests driver creation, registration, and automatic detection.
"""

import pytest
from unittest.mock import MagicMock
from bleak import BLEDevice

from core.drivers.device_factory import DeviceFactory
from core.drivers.elk_bledom import ElkBledomDriver
from core.drivers.triones import TrionesDriver
from core.drivers.magichome import MagicHomeDriver
from core.drivers.tuya import TuyaDriver


class TestDeviceFactory:
    """Tests for DeviceFactory."""
    
    def test_create_driver_explicit_elk_bledom(self):
        """Test explicit ELK-BLEDOM driver creation."""
        driver = DeviceFactory.create_driver(protocol_type="elk_bledom")
        assert isinstance(driver, ElkBledomDriver)
    
    def test_create_driver_explicit_aliases(self):
        """Test driver creation with aliases."""
        assert isinstance(DeviceFactory.create_driver(protocol_type="elk"), ElkBledomDriver)
        assert isinstance(DeviceFactory.create_driver(protocol_type="bledom"), ElkBledomDriver)
        assert isinstance(DeviceFactory.create_driver(protocol_type="triones"), TrionesDriver)
        assert isinstance(DeviceFactory.create_driver(protocol_type="magichome"), MagicHomeDriver)
        assert isinstance(DeviceFactory.create_driver(protocol_type="magic"), MagicHomeDriver)
        assert isinstance(DeviceFactory.create_driver(protocol_type="tuya"), TuyaDriver)
    
    def test_create_driver_unknown_protocol(self):
        """Test error on unknown protocol."""
        with pytest.raises(ValueError, match="Unknown protocol"):
            DeviceFactory.create_driver(protocol_type="unknown_protocol")
    
    def test_create_driver_auto_detect_elk_bledom(self):
        """Test automatic detection of ELK-BLEDOM device."""
        mock_device = MagicMock(spec=BLEDevice)
        mock_device.name = "ELK-BLEDOM Controller"
        mock_device.address = "00:11:22:33:44:55"
        mock_device.metadata = {"uuids": []}
        
        driver = DeviceFactory.create_driver(device=mock_device)
        assert isinstance(driver, ElkBledomDriver)
    
    def test_create_driver_auto_detect_triones(self):
        """Test automatic detection of Triones device."""
        mock_device = MagicMock(spec=BLEDevice)
        mock_device.name = "Triones Controller"
        mock_device.address = "00:11:22:33:44:55"
        mock_device.metadata = {"uuids": []}
        
        driver = DeviceFactory.create_driver(device=mock_device)
        assert isinstance(driver, TrionesDriver)
    
    def test_create_driver_auto_detect_magichome(self):
        """Test automatic detection of MagicHome device."""
        mock_device = MagicMock(spec=BLEDevice)
        mock_device.name = "MagicHome Controller"
        mock_device.address = "00:11:22:33:44:55"
        mock_device.metadata = {"uuids": []}
        
        driver = DeviceFactory.create_driver(device=mock_device)
        assert isinstance(driver, MagicHomeDriver)
    
    def test_create_driver_auto_detect_tuya(self):
        """Test automatic detection of Tuya device."""
        mock_device = MagicMock(spec=BLEDevice)
        mock_device.name = "Tuya Controller"
        mock_device.address = "00:11:22:33:44:55"
        mock_device.metadata = {"uuids": []}
        
        driver = DeviceFactory.create_driver(device=mock_device)
        assert isinstance(driver, TuyaDriver)
    
    def test_create_driver_auto_detect_by_uuid(self):
        """Test automatic detection by UUID."""
        # Test Triones UUID
        mock_device = MagicMock(spec=BLEDevice)
        mock_device.name = "Unknown Device"
        mock_device.address = "00:11:22:33:44:55"
        mock_device.metadata = {
            "uuids": ["0000ffd9-0000-1000-8000-00805f9b34fb"]
        }
        
        driver = DeviceFactory.create_driver(device=mock_device)
        assert isinstance(driver, TrionesDriver)
        
        # Test MagicHome UUID
        mock_device.metadata = {
            "uuids": ["0000ffe5-0000-1000-8000-00805f9b34fb"]
        }
        driver = DeviceFactory.create_driver(device=mock_device)
        assert isinstance(driver, MagicHomeDriver)
        
        # Test Tuya UUID
        mock_device.metadata = {
            "uuids": ["0000fe95-0000-1000-8000-00805f9b34fb"]
        }
        driver = DeviceFactory.create_driver(device=mock_device)
        assert isinstance(driver, TuyaDriver)
    
    def test_create_driver_fallback_to_elk_bledom(self):
        """Test fallback to ELK-BLEDOM for generic LED devices."""
        mock_device = MagicMock(spec=BLEDevice)
        mock_device.name = "RGB LED Controller"
        mock_device.address = "00:11:22:33:44:55"
        mock_device.metadata = {"uuids": []}
        
        driver = DeviceFactory.create_driver(device=mock_device)
        assert isinstance(driver, ElkBledomDriver)
    
    def test_create_driver_no_device_or_protocol(self):
        """Test error when neither device nor protocol provided."""
        with pytest.raises(ValueError, match="Either protocol_type or device"):
            DeviceFactory.create_driver()
    
    def test_create_driver_unknown_device(self):
        """Test error when device cannot be detected."""
        mock_device = MagicMock(spec=BLEDevice)
        mock_device.name = "Completely Unknown Device"
        mock_device.address = "00:11:22:33:44:55"
        mock_device.metadata = {"uuids": []}
        
        with pytest.raises(ValueError, match="Could not detect protocol"):
            DeviceFactory.create_driver(device=mock_device)
    
    def test_get_available_protocols(self):
        """Test getting list of available protocols."""
        protocols = DeviceFactory.get_available_protocols()
        
        assert "elk_bledom" in protocols
        assert "elk" in protocols
        assert "bledom" in protocols
        assert "triones" in protocols
        assert "magichome" in protocols
        assert "tuya" in protocols
        assert isinstance(protocols, list)
        assert len(protocols) > 0
    
    def test_is_protocol_supported(self):
        """Test protocol support check."""
        assert DeviceFactory.is_protocol_supported("elk_bledom") is True
        assert DeviceFactory.is_protocol_supported("triones") is True
        assert DeviceFactory.is_protocol_supported("magichome") is True
        assert DeviceFactory.is_protocol_supported("tuya") is True
        assert DeviceFactory.is_protocol_supported("unknown") is False
        
        # Case insensitive
        assert DeviceFactory.is_protocol_supported("ELK_BLEDOM") is True
        assert DeviceFactory.is_protocol_supported("Triones") is True
    
    def test_register_driver(self):
        """Test registering a new driver."""
        # Create a mock driver class
        class MockDriver(ElkBledomDriver):
            pass
        
        DeviceFactory.register_driver("mock", MockDriver)
        
        assert DeviceFactory.is_protocol_supported("mock") is True
        driver = DeviceFactory.create_driver(protocol_type="mock")
        assert isinstance(driver, MockDriver)
    
    def test_detection_order(self):
        """Test that detection order is respected."""
        # Create devices that could match multiple drivers
        # Triones should be detected first
        mock_device = MagicMock(spec=BLEDevice)
        mock_device.name = "Triones LED Controller"  # Contains "LED" but also "Triones"
        mock_device.address = "00:11:22:33:44:55"
        mock_device.metadata = {"uuids": []}
        
        driver = DeviceFactory.create_driver(device=mock_device)
        # Should detect as Triones, not fallback to ELK-BLEDOM
        assert isinstance(driver, TrionesDriver)

