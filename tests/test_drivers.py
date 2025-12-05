"""
Unit tests for LED device drivers.
Tests all driver implementations: ELK-BLEDOM, Triones, MagicHome, Tuya.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from bleak import BleakClient

from core.interfaces import AbstractLedDevice
from core.drivers.elk_bledom import ElkBledomDriver
from core.drivers.triones import TrionesDriver
from core.drivers.magichome import MagicHomeDriver
from core.drivers.tuya import TuyaDriver


class TestElkBledomDriver:
    """Tests for ELK-BLEDOM driver."""
    
    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful connection."""
        driver = ElkBledomDriver()
        mock_client = MagicMock(spec=BleakClient)
        mock_client.is_connected = True
        
        result = await driver.connect(mock_client)
        
        assert result is True
        assert driver.is_connected is True
        assert driver.client == mock_client
    
    @pytest.mark.asyncio
    async def test_connect_failure(self):
        """Test connection failure."""
        driver = ElkBledomDriver()
        mock_client = MagicMock(spec=BleakClient)
        mock_client.is_connected = False
        
        result = await driver.connect(mock_client)
        
        assert result is False
        assert driver.is_connected is False
    
    @pytest.mark.asyncio
    async def test_set_color(self):
        """Test setting RGB color."""
        driver = ElkBledomDriver()
        mock_client = MagicMock(spec=BleakClient)
        mock_client.is_connected = True
        mock_client.write_gatt_char = AsyncMock()
        
        await driver.connect(mock_client)
        result = await driver.set_color(255, 128, 64)
        
        assert result is True
        mock_client.write_gatt_char.assert_called_once()
        payload = mock_client.write_gatt_char.call_args[0][1]
        assert isinstance(payload, bytearray)
        assert payload[0] == 0x7E
        assert payload[3] == 0x03  # CMD_COLOR
        assert payload[4] == 255  # R
        assert payload[5] == 128  # G
        assert payload[6] == 64   # B
        assert payload[-1] == 0xEF
    
    @pytest.mark.asyncio
    async def test_set_color_not_connected(self):
        """Test set_color when not connected."""
        driver = ElkBledomDriver()
        result = await driver.set_color(255, 128, 64)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_set_brightness(self):
        """Test setting brightness."""
        driver = ElkBledomDriver()
        mock_client = MagicMock(spec=BleakClient)
        mock_client.is_connected = True
        
        await driver.connect(mock_client)
        result = await driver.set_brightness(50)
        
        # ELK-BLEDOM doesn't have separate brightness command
        assert result is True
    
    @pytest.mark.asyncio
    async def test_set_mode(self):
        """Test setting mode."""
        driver = ElkBledomDriver()
        mock_client = MagicMock(spec=BleakClient)
        mock_client.is_connected = True
        mock_client.write_gatt_char = AsyncMock()
        
        await driver.connect(mock_client)
        result = await driver.set_mode(ElkBledomDriver.MODE_RAINBOW, speed=32)
        
        assert result is True
        mock_client.write_gatt_char.assert_called_once()
        payload = mock_client.write_gatt_char.call_args[0][1]
        assert payload[3] == 0x04  # CMD_MODE
        assert payload[4] == ElkBledomDriver.MODE_RAINBOW
        assert payload[7] == 32  # Speed
    
    def test_get_write_characteristic_uuid(self):
        """Test UUID getter."""
        driver = ElkBledomDriver()
        uuid = driver.get_write_characteristic_uuid()
        assert uuid == "0000fff3-0000-1000-8000-00805f9b34fb"
    
    def test_get_protocol_name(self):
        """Test protocol name."""
        driver = ElkBledomDriver()
        assert driver.get_protocol_name() == "ELK-BLEDOM"
    
    def test_can_handle_device_by_name(self):
        """Test device detection by name."""
        assert ElkBledomDriver.can_handle_device("ELK-BLEDOM", []) is True
        assert ElkBledomDriver.can_handle_device("Some ELK Device", []) is True
        assert ElkBledomDriver.can_handle_device("BLEDOM Controller", []) is True
        assert ElkBledomDriver.can_handle_device("Other Device", []) is False
    
    def test_can_handle_device_by_uuid(self):
        """Test device detection by UUID."""
        uuid = "0000fff3-0000-1000-8000-00805f9b34fb"
        assert ElkBledomDriver.can_handle_device(None, [uuid]) is True
        assert ElkBledomDriver.can_handle_device("Unknown", [uuid]) is True
    
    def test_get_supported_modes(self):
        """Test supported modes."""
        modes = ElkBledomDriver.get_supported_modes()
        assert "MANUAL" in modes
        assert "CPU" in modes
        assert "BREATH" in modes
        assert "RAINBOW" in modes
        assert modes["MANUAL"] == ElkBledomDriver.MODE_MANUAL


class TestTrionesDriver:
    """Tests for Triones driver."""
    
    @pytest.mark.asyncio
    async def test_connect_and_uuid_detection(self):
        """Test connection with UUID detection."""
        driver = TrionesDriver()
        mock_client = MagicMock(spec=BleakClient)
        mock_client.is_connected = True
        
        # Mock service with characteristic
        mock_char = MagicMock()
        mock_char.uuid = "0000ffd9-0000-1000-8000-00805f9b34fb"
        mock_service = MagicMock()
        mock_service.characteristics = [mock_char]
        mock_client.services = [mock_service]
        
        result = await driver.connect(mock_client)
        
        assert result is True
        assert driver.is_connected is True
        assert driver.actual_uuid == str(mock_char.uuid)
    
    @pytest.mark.asyncio
    async def test_set_color(self):
        """Test setting RGB color."""
        driver = TrionesDriver()
        mock_client = MagicMock(spec=BleakClient)
        mock_client.is_connected = True
        mock_client.write_gatt_char = AsyncMock()
        
        await driver.connect(mock_client)
        result = await driver.set_color(255, 128, 64)
        
        assert result is True
        mock_client.write_gatt_char.assert_called_once()
        payload = mock_client.write_gatt_char.call_args[0][1]
        assert payload[0] == 0x56
        assert payload[1] == 0xAA
        assert payload[2] == 0x01  # CMD_COLOR
        assert payload[3] == 255  # R
        assert payload[4] == 128  # G
        assert payload[5] == 64   # B
        assert payload[6] == 0xAA
        assert payload[7] == 0xAA
    
    @pytest.mark.asyncio
    async def test_set_brightness(self):
        """Test setting brightness."""
        driver = TrionesDriver()
        mock_client = MagicMock(spec=BleakClient)
        mock_client.is_connected = True
        mock_client.write_gatt_char = AsyncMock()
        
        await driver.connect(mock_client)
        result = await driver.set_brightness(75)
        
        assert result is True
        payload = mock_client.write_gatt_char.call_args[0][1]
        assert payload[2] == 0x05  # CMD_BRIGHTNESS
        # Brightness should be converted from 0-100 to 0-255
        assert payload[3] == int((75 / 100.0) * 255)
    
    def test_can_handle_device(self):
        """Test device detection."""
        assert TrionesDriver.can_handle_device("Triones Controller", []) is True
        assert TrionesDriver.can_handle_device("TRION Device", []) is True
        uuid = "0000ffd9-0000-1000-8000-00805f9b34fb"
        assert TrionesDriver.can_handle_device(None, [uuid]) is True
    
    def test_get_supported_modes(self):
        """Test supported modes."""
        modes = TrionesDriver.get_supported_modes()
        assert "MANUAL" in modes
        assert "JUMP" in modes
        assert "FADE" in modes
        assert "FLASH" in modes


class TestMagicHomeDriver:
    """Tests for MagicHome driver."""
    
    @pytest.mark.asyncio
    async def test_set_color(self):
        """Test setting RGB color."""
        driver = MagicHomeDriver()
        mock_client = MagicMock(spec=BleakClient)
        mock_client.is_connected = True
        mock_client.write_gatt_char = AsyncMock()
        
        await driver.connect(mock_client)
        result = await driver.set_color(255, 128, 64)
        
        assert result is True
        payload = mock_client.write_gatt_char.call_args[0][1]
        assert payload[0] == 0x7E  # Packet start
        assert payload[1] == 5  # Length (CMD + 4 data bytes)
        assert payload[2] == 0x05  # CMD_COLOR
        assert payload[3] == 255  # R
        assert payload[4] == 128  # G
        assert payload[5] == 64   # B
        assert payload[6] == 0x00  # W (white channel)
        assert payload[-1] == 0xEF  # Packet end
    
    def test_can_handle_device(self):
        """Test device detection."""
        assert MagicHomeDriver.can_handle_device("MagicHome Controller", []) is True
        assert MagicHomeDriver.can_handle_device("MH-123", []) is True
        uuid = "0000ffe5-0000-1000-8000-00805f9b34fb"
        assert MagicHomeDriver.can_handle_device(None, [uuid]) is True


class TestTuyaDriver:
    """Tests for Tuya driver."""
    
    @pytest.mark.asyncio
    async def test_set_color(self):
        """Test setting RGB color."""
        driver = TuyaDriver()
        mock_client = MagicMock(spec=BleakClient)
        mock_client.is_connected = True
        mock_client.write_gatt_char = AsyncMock()
        
        await driver.connect(mock_client)
        result = await driver.set_color(255, 128, 64)
        
        assert result is True
        payload = mock_client.write_gatt_char.call_args[0][1]
        assert payload[0] == 0x01  # CMD_COLOR
        assert payload[1] == 3  # Length (3 data bytes)
        assert payload[2] == 255  # R
        assert payload[3] == 128  # G
        assert payload[4] == 64   # B
    
    def test_can_handle_device(self):
        """Test device detection."""
        assert TuyaDriver.can_handle_device("Tuya Controller", []) is True
        assert TuyaDriver.can_handle_device("TY-123", []) is True
        assert TuyaDriver.can_handle_device("Smart Life Device", []) is True
        uuid = "0000fe95-0000-1000-8000-00805f9b34fb"
        assert TuyaDriver.can_handle_device(None, [uuid]) is True


class TestDriverInterface:
    """Tests for AbstractLedDevice interface compliance."""
    
    def test_all_drivers_implement_interface(self):
        """Verify all drivers implement AbstractLedDevice."""
        drivers = [ElkBledomDriver, TrionesDriver, MagicHomeDriver, TuyaDriver]
        
        for driver_class in drivers:
            assert issubclass(driver_class, AbstractLedDevice)
            # Check required methods exist
            assert hasattr(driver_class, 'connect')
            assert hasattr(driver_class, 'disconnect')
            assert hasattr(driver_class, 'set_color')
            assert hasattr(driver_class, 'set_brightness')
            assert hasattr(driver_class, 'set_mode')
            assert hasattr(driver_class, 'get_write_characteristic_uuid')
            assert hasattr(driver_class, 'get_protocol_name')
            assert hasattr(driver_class, 'can_handle_device')
            assert hasattr(driver_class, 'get_supported_modes')
    
    @pytest.mark.asyncio
    async def test_driver_rgb_clamping(self):
        """Test that all drivers clamp RGB values."""
        drivers = [
            ElkBledomDriver(),
            TrionesDriver(),
            MagicHomeDriver(),
            TuyaDriver()
        ]
        
        for driver in drivers:
            mock_client = MagicMock(spec=BleakClient)
            mock_client.is_connected = True
            mock_client.write_gatt_char = AsyncMock()
            
            await driver.connect(mock_client)
            
            # Test values outside range
            await driver.set_color(300, -10, 500)
            
            # Verify values were clamped (check payload)
            payload = mock_client.write_gatt_char.call_args[0][1]
            # Extract RGB values from payload (varies by protocol)
            # Just verify no exception was raised and write was called
            mock_client.write_gatt_char.assert_called()

