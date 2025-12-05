"""
Triones protocol driver implementation.
Handles communication with Triones compatible LED controllers.

Protocol details (based on common Triones implementations):
- Write UUID: 0000ffd9-0000-1000-8000-00805f9b34fb (common variant)
- Alternative UUID: 0000ffd5-0000-1000-8000-00805f9b34fb
- Packet format: [0x56, 0xAA, CMD, P1, P2, P3, 0xAA, 0xAA] or variant
- Color command: CMD=0x01, P1=R, P2=G, P3=B
"""

from typing import Optional
from bleak import BleakClient

from core.interfaces import AbstractLedDevice


class TrionesDriver(AbstractLedDevice):
    """
    Driver for Triones protocol.
    
    Note: Triones protocol has multiple variants. This implementation
    uses the most common format. May require adjustment for specific devices.
    """
    
    # Common Triones UUIDs (may vary by device model)
    WRITE_CHAR_UUID = "0000ffd9-0000-1000-8000-00805f9b34fb"
    ALTERNATIVE_UUID = "0000ffd5-0000-1000-8000-00805f9b34fb"
    
    # Packet constants
    PACKET_START = bytearray([0x56, 0xAA])
    PACKET_END = bytearray([0xAA, 0xAA])
    
    # Command codes
    CMD_COLOR = 0x01
    CMD_MODE = 0x04
    CMD_BRIGHTNESS = 0x05
    CMD_POWER = 0x02
    
    # Mode IDs (common Triones modes)
    MODE_STATIC = 0x01
    MODE_JUMP = 0x02
    MODE_FADE = 0x03
    MODE_FLASH = 0x04
    
    def __init__(self, client: Optional[BleakClient] = None):
        super().__init__(client)
        self.current_speed: int = 0x20  # Default speed
        self.actual_uuid: Optional[str] = None  # Will be determined on connect
    
    async def connect(self, client: BleakClient) -> bool:
        """Establish connection to Triones device."""
        try:
            self.client = client
            if client.is_connected:
                # Try to determine correct UUID by checking available characteristics
                try:
                    services = client.services
                    for service in services:
                        for char in service.characteristics:
                            char_uuid = str(char.uuid).lower()
                            if "ffd9" in char_uuid or "ffd5" in char_uuid:
                                self.actual_uuid = str(char.uuid)
                                break
                except Exception:
                    pass
                
                # Fallback to default UUID
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
    
    def _build_packet(self, cmd: int, p1: int = 0, p2: int = 0, p3: int = 0) -> bytearray:
        """
        Build Triones protocol packet.
        
        Format: [0x56, 0xAA, CMD, P1, P2, P3, 0xAA, 0xAA]
        """
        return bytearray([
            *self.PACKET_START,
            cmd & 0xFF,
            p1 & 0xFF,
            p2 & 0xFF,
            p3 & 0xFF,
            *self.PACKET_END
        ])
    
    async def set_color(self, r: int, g: int, b: int) -> bool:
        """Set RGB color on Triones device."""
        if not self.client or not self.client.is_connected:
            return False
        
        try:
            # Clamp RGB values
            r = max(0, min(255, int(r)))
            g = max(0, min(255, int(g)))
            b = max(0, min(255, int(b)))
            
            payload = self._build_packet(
                cmd=self.CMD_COLOR,
                p1=r,
                p2=g,
                p3=b
            )
            
            uuid = self.actual_uuid or self.WRITE_CHAR_UUID
            await self.client.write_gatt_char(
                uuid,
                payload,
                response=False
            )
            return True
        except Exception:
            # Try alternative UUID if first attempt fails
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
        
        Triones uses separate brightness command.
        """
        if not self.client or not self.client.is_connected:
            return False
        
        try:
            # Convert 0-100 to 0-255 range
            brightness_val = max(0, min(100, int(brightness)))
            brightness_byte = int((brightness_val / 100.0) * 255)
            
            payload = self._build_packet(
                cmd=self.CMD_BRIGHTNESS,
                p1=brightness_byte,
                p2=0x00,
                p3=0x00
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
        Set effect mode on Triones device.
        
        Args:
            mode_id: Mode identifier (MODE_STATIC, MODE_JUMP, MODE_FADE, MODE_FLASH)
            speed: Effect speed (0-255). If 0, uses current speed.
        """
        if not self.client or not self.client.is_connected:
            return False
        
        try:
            if speed > 0:
                self.current_speed = max(0, min(255, int(speed)))
            
            payload = self._build_packet(
                cmd=self.CMD_MODE,
                p1=mode_id & 0xFF,
                p2=self.current_speed & 0xFF,
                p3=0x00
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
        """Get write characteristic UUID for Triones."""
        return self.WRITE_CHAR_UUID
    
    def get_protocol_name(self) -> str:
        """Get protocol name."""
        return "Triones"
    
    @staticmethod
    def can_handle_device(device_name: Optional[str], service_uuids: list) -> bool:
        """
        Check if device is Triones compatible.
        
        Detection criteria:
        - Device name contains "Triones" or "TRIONES"
        - Service UUIDs contain ffd9 or ffd5
        """
        if device_name:
            name_upper = device_name.upper()
            if "TRIONES" in name_upper or "TRION" in name_upper:
                return True
        
        # Check for characteristic UUID in services
        uuid_strs = [
            TrionesDriver.WRITE_CHAR_UUID.lower(),
            TrionesDriver.ALTERNATIVE_UUID.lower()
        ]
        for uuid in service_uuids:
            uuid_lower = str(uuid).lower()
            if any(uuid_str in uuid_lower for uuid_str in uuid_strs):
                return True
            # Check for common Triones UUID patterns
            if "ffd9" in uuid_lower or "ffd5" in uuid_lower:
                return True
        
        return False
    
    @staticmethod
    def get_supported_modes() -> dict:
        """Get supported mode mappings for Triones."""
        return {
            "MANUAL": TrionesDriver.MODE_STATIC,
            "JUMP": TrionesDriver.MODE_JUMP,
            "FADE": TrionesDriver.MODE_FADE,
            "FLASH": TrionesDriver.MODE_FLASH,
            # Map common modes to Triones modes
            "CPU": TrionesDriver.MODE_FADE,  # Use fade as approximation
            "BREATH": TrionesDriver.MODE_FADE,
            "RAINBOW": TrionesDriver.MODE_JUMP
        }
    
    def set_speed(self, speed: int) -> None:
        """Set effect speed (0-255)."""
        self.current_speed = max(0, min(255, int(speed)))

