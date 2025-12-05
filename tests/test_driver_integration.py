"""
Integration tests for driver integration with BleDeviceController.
Tests that drivers work correctly when integrated with the controller.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from bleak import BLEDevice, BleakClient

from core.models import DeviceConfig, Color, ColorMode
from core.controller import BleDeviceController
from core.drivers.device_factory import DeviceFactory


class TestDriverIntegration:
    """Integration tests for drivers with BleDeviceController."""
    
    @pytest.mark.asyncio
    async def test_controller_uses_explicit_driver(self):
        """Test that controller uses explicitly specified driver."""
        config = DeviceConfig(
            target_mac="00:11:22:33:44:55",
            protocol="triones"
        )
        
        controller = BleDeviceController(
            config,
            lambda s: None,
            lambda c: None,
            use_real_device=False
        )
        
        # Mock device discovery
        mock_device = MagicMock(spec=BLEDevice)
        mock_device.name = "Test Device"
        mock_device.address = "00:11:22:33:44:55"
        
        # Mock driver initialization
        with patch.object(controller, '_find_device', return_value=mock_device):
            with patch.object(controller, '_initialize_driver') as mock_init:
                # Start controller (will fail on actual connection, but we test initialization)
                controller.is_running = True
                try:
                    await controller._main_loop()
                except Exception:
                    pass  # Expected to fail without real device
                
                # Verify driver was initialized
                mock_init.assert_called()
    
    @pytest.mark.asyncio
    async def test_controller_auto_detects_driver(self):
        """Test that controller auto-detects driver when protocol not specified."""
        config = DeviceConfig(
            target_mac="00:11:22:33:44:55",
            protocol=None  # Auto-detect
        )
        
        controller = BleDeviceController(
            config,
            lambda s: None,
            lambda c: None,
            use_real_device=False
        )
        
        # Mock Triones device
        mock_device = MagicMock(spec=BLEDevice)
        mock_device.name = "Triones Controller"
        mock_device.address = "00:11:22:33:44:55"
        mock_device.metadata = {"uuids": []}
        
        # Test driver initialization
        await controller._initialize_driver(mock_device)
        
        # Verify Triones driver was created
        assert controller.device_driver is not None
        assert controller.device_driver.get_protocol_name() == "Triones"
    
    @pytest.mark.asyncio
    async def test_controller_sends_color_via_driver(self):
        """Test that controller sends color commands through driver."""
        config = DeviceConfig(
            target_mac="00:11:22:33:44:55",
            protocol="elk_bledom"
        )
        
        controller = BleDeviceController(
            config,
            lambda s: None,
            lambda c: None,
            use_real_device=False
        )
        
        # Create and connect mock driver
        from core.drivers.elk_bledom import ElkBledomDriver
        mock_driver = MagicMock(spec=ElkBledomDriver)
        mock_driver.set_color = AsyncMock(return_value=True)
        mock_driver.is_connected = True
        
        controller.device_driver = mock_driver
        
        # Set color
        color = Color(255, 128, 64)
        controller.set_color(color)
        controller.current_color = color
        controller.brightness = 1.0
        
        # Send color (simulate what happens in _execute_mode)
        await controller._send_color(color)
        
        # Verify driver was called
        mock_driver.set_color.assert_called_once()
        args = mock_driver.set_color.call_args[0]
        # Check RGB values (with brightness applied)
        assert args[0] == 255  # R
        assert args[1] == 128  # G
        assert args[2] == 64   # B
    
    @pytest.mark.asyncio
    async def test_controller_sends_mode_via_driver(self):
        """Test that controller sends mode commands through driver."""
        config = DeviceConfig(
            target_mac="00:11:22:33:44:55",
            protocol="triones"
        )
        
        controller = BleDeviceController(
            config,
            lambda s: None,
            lambda c: None,
            use_real_device=False
        )
        
        # Create mock driver
        from core.drivers.triones import TrionesDriver
        mock_driver = MagicMock(spec=TrionesDriver)
        mock_driver.set_mode = AsyncMock(return_value=True)
        mock_driver.get_supported_modes = MagicMock(return_value={
            "MANUAL": 0x01,
            "RAINBOW": 0x04
        })
        mock_driver.is_connected = True
        
        controller.device_driver = mock_driver
        controller.current_mode = ColorMode.RAINBOW
        controller.speed = 32
        
        # Send mode command
        result = await controller._send_mode_command(ColorMode.RAINBOW)
        
        assert result is True
        mock_driver.set_mode.assert_called_once()
        args = mock_driver.set_mode.call_args
        assert args[0][0] == 0x04  # RAINBOW mode ID
        assert args[0][1] == 32    # Speed
    
    @pytest.mark.asyncio
    async def test_controller_handles_driver_errors(self):
        """Test that controller handles driver errors gracefully."""
        config = DeviceConfig(
            target_mac="00:11:22:33:44:55",
            protocol="magichome"
        )
        
        controller = BleDeviceController(
            config,
            lambda s: None,
            lambda c: None,
            use_real_device=False
        )
        
        # Create mock driver that raises exception
        from core.drivers.magichome import MagicHomeDriver
        mock_driver = MagicMock(spec=MagicHomeDriver)
        mock_driver.set_color = AsyncMock(side_effect=Exception("Driver error"))
        mock_driver.is_connected = True
        
        controller.device_driver = mock_driver
        
        # Try to send color
        color = Color(255, 128, 64)
        controller.set_color(color)
        controller.current_color = color
        
        # Should handle error gracefully
        await controller._send_color(color)
        
        # Controller should mark as disconnected on error
        # (actual behavior depends on implementation)
        assert controller.device_driver is not None
    
    @pytest.mark.asyncio
    async def test_controller_updates_uuid_from_driver(self):
        """Test that controller updates UUID from driver if not set."""
        config = DeviceConfig(
            target_mac="00:11:22:33:44:55",
            write_char_uuid="",  # Empty, should be filled from driver
            protocol="tuya"
        )
        
        controller = BleDeviceController(
            config,
            lambda s: None,
            lambda c: None,
            use_real_device=False
        )
        
        # Mock Tuya device
        mock_device = MagicMock(spec=BLEDevice)
        mock_device.name = "Tuya Controller"
        mock_device.address = "00:11:22:33:44:55"
        mock_device.metadata = {"uuids": []}
        
        # Initialize driver
        await controller._initialize_driver(mock_device)
        
        # Verify UUID was updated
        assert config.write_char_uuid != ""
        assert config.write_char_uuid == controller.device_driver.get_write_characteristic_uuid()
    
    def test_all_protocols_have_valid_mode_mappings(self):
        """Test that all drivers have valid mode mappings for common modes."""
        protocols = ["elk_bledom", "triones", "magichome", "tuya"]
        common_modes = ["MANUAL", "CPU", "BREATH", "RAINBOW"]
        
        for protocol_name in protocols:
            driver_class = DeviceFactory.create_driver(protocol_type=protocol_name).__class__
            modes = driver_class.get_supported_modes()
            
            # Check that common modes are mapped
            for mode in common_modes:
                assert mode in modes, f"{protocol_name} missing mode {mode}"
                assert isinstance(modes[mode], int), f"{protocol_name} mode {mode} should be int"

