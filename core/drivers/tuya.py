"""
Tuya protocol driver implementation.
Handles communication with Tuya compatible LED controllers.

Protocol details (based on common Tuya BLE implementations):
- Write UUID: 0000fe95-0000-1000-8000-00805f9b34fb (common variant)
- Alternative UUID: 0000fe40-0000-1000-8000-00805f9b34fb
- Packet format: Tuya-specific encrypted format or simple [CMD, DATA...]
- Note: Tuya protocol is complex and may require encryption/decryption
"""

from typing import Optional
from bleak import BleakClient

from core.interfaces import AbstractLedDevice


class TuyaDriver(AbstractLedDevice):
    """
    Driver for Tuya protocol.
    
    Note: Tuya protocol is complex and varies by device model.
    This is a basic implementation that may need enhancement for
    specific Tuya devices. Some Tuya devices use encrypted communication.
    """
    
    # Common Tuya UUIDs
    WRITE_CHAR_UUID = "0000fe95-0000-1000-8000-00805f9b34fb"
    ALTERNATIVE_UUID = "0000fe40-0000-1000-8000-00805f9b34fb"
    SERVICE_UUID = "0000fe95-0000-1000-8000-00805f9b34fb"
    
    # Command codes (basic Tuya commands, may vary)
    CMD_COLOR = 0x01
    CMD_MODE = 0x02
    CMD_BRIGHTNESS = 0x03
    CMD_POWER = 0x04
    
    # Mode IDs (common Tuya modes)
    MODE_STATIC = 0x01
    MODE_JUMP = 0x02
    MODE_FADE = 0x03
    MODE_FLASH = 0x04
    
    def __init__(self, client: Optional[BleakClient] = None):
        super().__init__(client)
        self.current_speed: int = 0x20  # Default speed
        self.actual_uuid: Optional[str] = None
    
    async def connect(self, client: BleakClient) -> bool:
        """Establish connection to Tuya device."""
        try:
            self.client = client
            if client.is_connected:
                # Try to determine correct UUID
                try:
                    services = client.services
                    for service in services:
                        for char in service.characteristics:
                            char_uuid = str(char.uuid).lower()
                            if "fe95" in char_uuid or "fe40" in char_uuid:
                                self.actual_uuid = str(char.uuid)
                                break
                except Exception:
                    pass
                
                if not self.actual_uuid:
                    self.actual_uuid = self.WRITE_CHAR_UUID
                
                self.is_connected = True
                return True
            return False
        except Exception:
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from device."""
        self.is_connected = False
        self.client = None
        self.actual_uuid = None
    
    def _build_simple_packet(self, cmd: int, data: list) -> bytearray:
        """
        Build simple Tuya packet (non-encrypted variant).
        
        Format: [CMD, LEN, DATA...]
        Some Tuya devices use simpler format without encryption.
        """
        data_bytes = [d & 0xFF for d in data]
        return bytearray([
            cmd & 0xFF,
            len(data_bytes) & 0xFF,
            *data_bytes
        ])
    
    async def set_color(self, r: int, g: int, b: int) -> bool:
        """Set RGB color on Tuya device."""
        if not self.client or not self.client.is_connected:
            return False
        
        try:
            # Clamp RGB values
            r = max(0, min(255, int(r)))
            g = max(0, min(255, int(g)))
            b = max(0, min(255, int(b)))
            
            # Simple Tuya color packet: [CMD, LEN, R, G, B]
            payload = self._build_simple_packet(
                cmd=self.CMD_COLOR,
                data=[r, g, b]
            )
            
            uuid = self.actual_uuid or self.WRITE_CHAR_UUID
            await self.client.write_gatt_char(
                uuid,
                payload,
                response=False
            )
            return True
        except Exception:
            # Try alternative UUID
            if self.actual_uuid != self.ALTERNATIVE_UUID:
                try:
                    self.actual_uuid = self.ALTERNATIVE_UUID
                    uuid = self.ALTERNATIVE_UUID
                    await self.client.write_gatt_char(
                        uuid,
                        payload,
                        response=False
                    )
                    return True
                except Exception:
                    pass
            return False
    
    async def set_brightness(self, brightness: int) -> bool:
        """
        Set brightness level (0-100).
        
        Tuya brightness may be separate command or part of color command.
        """
        if not self.client or not self.client.is_connected:
            return False
        
        try:
            brightness_val = max(0, min(100, int(brightness)))
            brightness_byte = int((brightness_val / 100.0) * 255)
            
            payload = self._build_simple_packet(
                cmd=self.CMD_BRIGHTNESS,
                data=[brightness_byte]
            )
            
            uuid = self.actual_uuid or self.WRITE_CHAR_UUID
            await self.client.write_gatt_char(
                uuid,
                payload,
                response=False
            )
            return True
        except Exception:
            return False
    
    async def set_mode(self, mode_id: int, speed: int = 0) -> bool:
        """
        Set effect mode on Tuya device.
        
        Args:
            mode_id: Mode identifier
            speed: Effect speed (0-255). If 0, uses current speed.
        """
        if not self.client or not self.client.is_connected:
            return False
        
        try:
            if speed > 0:
                self.current_speed = max(0, min(255, int(speed)))
            
            payload = self._build_simple_packet(
                cmd=self.CMD_MODE,
                data=[mode_id & 0xFF, self.current_speed & 0xFF]
            )
            
            uuid = self.actual_uuid or self.WRITE_CHAR_UUID
            await self.client.write_gatt_char(
                uuid,
                payload,
                response=False
            )
            return True
        except Exception:
            return False
    
    def get_write_characteristic_uuid(self) -> str:
        """Get write characteristic UUID for Tuya."""
        return self.WRITE_CHAR_UUID
    
    def get_protocol_name(self) -> str:
        """Get protocol name."""
        return "Tuya"
    
    @staticmethod
    def can_handle_device(device_name: Optional[str], service_uuids: list) -> bool:
        """
        Check if device is Tuya compatible.
        
        Detection criteria:
        - Device name contains "Tuya", "TY", "Smart Life"
        - Service UUIDs contain fe95 or fe40
        """
        if device_name:
            name_upper = device_name.upper()
            if any(keyword in name_upper for keyword in ["TUYA", "TY-", "SMART LIFE", "SMARTLIFE"]):
                return True
        
        # Check for characteristic UUID in services
        uuid_strs = [
            TuyaDriver.WRITE_CHAR_UUID.lower(),
            TuyaDriver.ALTERNATIVE_UUID.lower(),
            TuyaDriver.SERVICE_UUID.lower()
        ]
        for uuid in service_uuids:
            uuid_lower = str(uuid).lower()
            if any(uuid_str in uuid_lower for uuid_str in uuid_strs):
                return True
            if "fe95" in uuid_lower or "fe40" in uuid_lower:
                return True
        
        return False
    
    @staticmethod
    def get_supported_modes() -> dict:
        """Get supported mode mappings for Tuya."""
        return {
            "MANUAL": TuyaDriver.MODE_STATIC,
            "JUMP": TuyaDriver.MODE_JUMP,
            "FADE": TuyaDriver.MODE_FADE,
            "FLASH": TuyaDriver.MODE_FLASH,
            # Map common modes
            "CPU": TuyaDriver.MODE_FADE,
            "BREATH": TuyaDriver.MODE_FADE,
            "RAINBOW": TuyaDriver.MODE_JUMP
        }
    
    def set_speed(self, speed: int) -> None:
        """Set effect speed (0-255)."""
        self.current_speed = max(0, min(255, int(speed)))

