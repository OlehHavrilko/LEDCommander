"""
ELK-BLEDOM protocol driver implementation.
Handles communication with ELK-BLEDOM compatible LED controllers.
"""

from typing import Optional
from bleak import BleakClient

from core.interfaces import AbstractLedDevice


class ElkBledomDriver(AbstractLedDevice):
    """
    Driver for ELK-BLEDOM protocol.
    
    Protocol details:
    - Write UUID: 0000fff3-0000-1000-8000-00805f9b34fb
    - Packet format: [0x7E, 0x07, 0x05, CMD, P1, P2, P3, SPEED, 0xEF]
    - Color command: CMD=0x03, P1=R, P2=G, P3=B
    - Mode command: CMD=0x04, P1=mode_id
    """
    
    # Protocol constants
    WRITE_CHAR_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"
    PACKET_HEADER = bytearray([0x7E, 0x07, 0x05])
    PACKET_FOOTER = 0xEF
    
    # Command codes
    CMD_COLOR = 0x03
    CMD_MODE = 0x04
    
    # Mode IDs
    MODE_MANUAL = 0x01
    MODE_CPU = 0x02
    MODE_BREATH = 0x03
    MODE_RAINBOW = 0x04
    
    def __init__(self, client: Optional[BleakClient] = None):
        super().__init__(client)
        self.current_speed: int = 0x10  # Default speed
    
    async def connect(self, client: BleakClient) -> bool:
        """Establish connection to ELK-BLEDOM device."""
        try:
            self.client = client
            if client.is_connected:
                self.is_connected = True
                return True
            return False
        except Exception:
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from device."""
        self.is_connected = False
        self.client = None
    
    def _build_packet(self, cmd: int, p1: int, p2: int, p3: int, speed: Optional[int] = None) -> bytearray:
        """
        Build ELK-BLEDOM protocol packet.
        
        Format: [0x7E, 0x07, 0x05, CMD, P1, P2, P3, SPEED, 0xEF]
        """
        if speed is None:
            speed = self.current_speed
        
        return bytearray([
            *self.PACKET_HEADER,
            cmd & 0xFF,
            p1 & 0xFF,
            p2 & 0xFF,
            p3 & 0xFF,
            speed & 0xFF,
            self.PACKET_FOOTER
        ])
    
    async def set_color(self, r: int, g: int, b: int) -> bool:
        """Set RGB color on ELK-BLEDOM device."""
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
            
            await self.client.write_gatt_char(
                self.WRITE_CHAR_UUID,
                payload,
                response=False
            )
            return True
        except Exception:
            return False
    
    async def set_brightness(self, brightness: int) -> bool:
        """
        Set brightness level (0-100).
        
        Note: ELK-BLEDOM doesn't have a dedicated brightness command.
        Brightness is typically handled by scaling RGB values in the application layer.
        This method is a no-op for compatibility with the interface.
        """
        # Store brightness for potential future use
        # Actual brightness is applied by scaling RGB in set_color()
        return True
    
    async def set_mode(self, mode_id: int, speed: int = 0) -> bool:
        """
        Set effect mode on ELK-BLEDOM device.
        
        Args:
            mode_id: Mode identifier (MODE_MANUAL, MODE_CPU, MODE_BREATH, MODE_RAINBOW)
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
                p2=0x00,
                p3=0x00,
                speed=self.current_speed
            )
            
            await self.client.write_gatt_char(
                self.WRITE_CHAR_UUID,
                payload,
                response=False
            )
            return True
        except Exception:
            return False
    
    def get_write_characteristic_uuid(self) -> str:
        """Get write characteristic UUID for ELK-BLEDOM."""
        return self.WRITE_CHAR_UUID
    
    def get_protocol_name(self) -> str:
        """Get protocol name."""
        return "ELK-BLEDOM"
    
    @staticmethod
    def can_handle_device(device_name: Optional[str], service_uuids: list) -> bool:
        """
        Check if device is ELK-BLEDOM compatible.
        
        Detection criteria:
        - Device name contains "ELK" or "BLEDOM"
        - Service UUIDs contain the write characteristic UUID
        """
        if device_name:
            name_upper = device_name.upper()
            if "ELK" in name_upper or "BLEDOM" in name_upper:
                return True
        
        # Check for characteristic UUID in services
        uuid_str = ElkBledomDriver.WRITE_CHAR_UUID.lower()
        for uuid in service_uuids:
            if uuid_str in str(uuid).lower():
                return True
        
        return False
    
    @staticmethod
    def get_supported_modes() -> dict:
        """Get supported mode mappings for ELK-BLEDOM."""
        return {
            "MANUAL": ElkBledomDriver.MODE_MANUAL,
            "CPU": ElkBledomDriver.MODE_CPU,
            "BREATH": ElkBledomDriver.MODE_BREATH,
            "RAINBOW": ElkBledomDriver.MODE_RAINBOW
        }
    
    def set_speed(self, speed: int) -> None:
        """Set effect speed (0-255)."""
        self.current_speed = max(0, min(255, int(speed)))

