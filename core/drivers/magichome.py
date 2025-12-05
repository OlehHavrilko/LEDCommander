"""
MagicHome protocol driver implementation.
Handles communication with MagicHome compatible LED controllers.

Protocol details (based on common MagicHome implementations):
- Write UUID: 0000ffe5-0000-1000-8000-00805f9b34fb (common variant)
- Alternative UUID: 0000ffe9-0000-1000-8000-00805f9b34fb
- Packet format varies by model, commonly: [0x7E, LEN, CMD, DATA..., 0xEF]
- Color command: CMD=0x05, DATA=[R, G, B, W, ...]
"""

from typing import Optional
from bleak import BleakClient

from core.interfaces import AbstractLedDevice


class MagicHomeDriver(AbstractLedDevice):
    """
    Driver for MagicHome protocol.
    
    Note: MagicHome has multiple variants and models. This implementation
    uses the most common format. May require adjustment for specific devices.
    """
    
    # Common MagicHome UUIDs
    WRITE_CHAR_UUID = "0000ffe5-0000-1000-8000-00805f9b34fb"
    ALTERNATIVE_UUID = "0000ffe9-0000-1000-8000-00805f9b34fb"
    
    # Packet constants
    PACKET_START = 0x7E
    PACKET_END = 0xEF
    
    # Command codes
    CMD_COLOR = 0x05
    CMD_MODE = 0x04
    CMD_BRIGHTNESS = 0x03
    CMD_POWER = 0x01
    
    # Mode IDs (common MagicHome modes)
    MODE_STATIC = 0x01
    MODE_JUMP = 0x02
    MODE_FADE = 0x03
    MODE_FLASH = 0x04
    
    def __init__(self, client: Optional[BleakClient] = None):
        super().__init__(client)
        self.current_speed: int = 0x20  # Default speed
        self.actual_uuid: Optional[str] = None
    
    async def connect(self, client: BleakClient) -> bool:
        """Establish connection to MagicHome device."""
        try:
            self.client = client
            if client.is_connected:
                # Try to determine correct UUID
                try:
                    services = client.services
                    for service in services:
                        for char in service.characteristics:
                            char_uuid = str(char.uuid).lower()
                            if "ffe5" in char_uuid or "ffe9" in char_uuid:
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
    
    def _build_packet(self, cmd: int, data: list) -> bytearray:
        """
        Build MagicHome protocol packet.
        
        Format: [0x7E, LEN, CMD, DATA..., 0xEF]
        """
        data_bytes = [d & 0xFF for d in data]
        length = len(data_bytes) + 1  # +1 for CMD byte
        
        return bytearray([
            self.PACKET_START,
            length & 0xFF,
            cmd & 0xFF,
            *data_bytes,
            self.PACKET_END
        ])
    
    async def set_color(self, r: int, g: int, b: int) -> bool:
        """Set RGB color on MagicHome device."""
        if not self.client or not self.client.is_connected:
            return False
        
        try:
            # Clamp RGB values
            r = max(0, min(255, int(r)))
            g = max(0, min(255, int(g)))
            b = max(0, min(255, int(b)))
            
            # MagicHome color packet: [R, G, B, W, ...]
            # W (white) is typically 0 for RGB-only strips
            payload = self._build_packet(
                cmd=self.CMD_COLOR,
                data=[r, g, b, 0x00]  # RGB + white channel
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
        
        MagicHome may use separate brightness command or scale RGB.
        """
        if not self.client or not self.client.is_connected:
            return False
        
        try:
            brightness_val = max(0, min(100, int(brightness)))
            brightness_byte = int((brightness_val / 100.0) * 255)
            
            payload = self._build_packet(
                cmd=self.CMD_BRIGHTNESS,
                data=[brightness_byte, 0x00, 0x00, 0x00]
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
        Set effect mode on MagicHome device.
        
        Args:
            mode_id: Mode identifier
            speed: Effect speed (0-255). If 0, uses current speed.
        """
        if not self.client or not self.client.is_connected:
            return False
        
        try:
            if speed > 0:
                self.current_speed = max(0, min(255, int(speed)))
            
            payload = self._build_packet(
                cmd=self.CMD_MODE,
                data=[mode_id & 0xFF, self.current_speed & 0xFF, 0x00, 0x00]
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
        """Get write characteristic UUID for MagicHome."""
        return self.WRITE_CHAR_UUID
    
    def get_protocol_name(self) -> str:
        """Get protocol name."""
        return "MagicHome"
    
    @staticmethod
    def can_handle_device(device_name: Optional[str], service_uuids: list) -> bool:
        """
        Check if device is MagicHome compatible.
        
        Detection criteria:
        - Device name contains "Magic", "MagicHome", "MH"
        - Service UUIDs contain ffe5 or ffe9
        """
        if device_name:
            name_upper = device_name.upper()
            if any(keyword in name_upper for keyword in ["MAGIC", "MAGICHOME", "MH-"]):
                return True
        
        # Check for characteristic UUID in services
        uuid_strs = [
            MagicHomeDriver.WRITE_CHAR_UUID.lower(),
            MagicHomeDriver.ALTERNATIVE_UUID.lower()
        ]
        for uuid in service_uuids:
            uuid_lower = str(uuid).lower()
            if any(uuid_str in uuid_lower for uuid_str in uuid_strs):
                return True
            if "ffe5" in uuid_lower or "ffe9" in uuid_lower:
                return True
        
        return False
    
    @staticmethod
    def get_supported_modes() -> dict:
        """Get supported mode mappings for MagicHome."""
        return {
            "MANUAL": MagicHomeDriver.MODE_STATIC,
            "JUMP": MagicHomeDriver.MODE_JUMP,
            "FADE": MagicHomeDriver.MODE_FADE,
            "FLASH": MagicHomeDriver.MODE_FLASH,
            # Map common modes
            "CPU": MagicHomeDriver.MODE_FADE,
            "BREATH": MagicHomeDriver.MODE_FADE,
            "RAINBOW": MagicHomeDriver.MODE_JUMP
        }
    
    def set_speed(self, speed: int) -> None:
        """Set effect speed (0-255)."""
        self.current_speed = max(0, min(255, int(speed)))

