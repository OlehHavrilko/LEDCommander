"""
Abstract interface for LED device drivers.
Defines the contract that all protocol-specific drivers must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
from bleak import BleakClient


class AbstractLedDevice(ABC):
    """
    Abstract base class for LED device drivers.
    
    All protocol-specific implementations (ELK-BLEDOM, Triones, MagicHome, Tuya)
    must inherit from this class and implement all abstract methods.
    """
    
    def __init__(self, client: Optional[BleakClient] = None):
        """
        Initialize device driver.
        
        Args:
            client: Optional BleakClient instance. If None, will be set during connect().
        """
        self.client: Optional[BleakClient] = client
        self.is_connected: bool = False
    
    @abstractmethod
    async def connect(self, client: BleakClient) -> bool:
        """
        Establish connection to the device.
        
        Args:
            client: BleakClient instance to use for communication.
            
        Returns:
            True if connection successful, False otherwise.
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from the device.
        """
        pass
    
    @abstractmethod
    async def set_color(self, r: int, g: int, b: int) -> bool:
        """
        Set RGB color on the device.
        
        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            
        Returns:
            True if command sent successfully, False otherwise.
        """
        pass
    
    @abstractmethod
    async def set_brightness(self, brightness: int) -> bool:
        """
        Set brightness level.
        
        Args:
            brightness: Brightness level (0-100)
            
        Returns:
            True if command sent successfully, False otherwise.
        """
        pass
    
    @abstractmethod
    async def set_mode(self, mode_id: int, speed: int = 0) -> bool:
        """
        Set effect mode on the device.
        
        Args:
            mode_id: Mode identifier (protocol-specific)
            speed: Effect speed (0-255, protocol-specific range)
            
        Returns:
            True if command sent successfully, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_write_characteristic_uuid(self) -> str:
        """
        Get the UUID of the GATT characteristic used for writing commands.
        
        Returns:
            UUID string (e.g., "0000fff3-0000-1000-8000-00805f9b34fb")
        """
        pass
    
    @abstractmethod
    def get_protocol_name(self) -> str:
        """
        Get human-readable protocol name.
        
        Returns:
            Protocol name (e.g., "ELK-BLEDOM", "Triones", "MagicHome")
        """
        pass
    
    @staticmethod
    @abstractmethod
    def can_handle_device(device_name: Optional[str], service_uuids: list) -> bool:
        """
        Check if this driver can handle a specific device.
        Used for automatic device detection (fingerprinting).
        
        Args:
            device_name: Device name from BLE advertisement
            service_uuids: List of service UUIDs advertised by the device
            
        Returns:
            True if this driver can handle the device, False otherwise.
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_supported_modes() -> dict:
        """
        Get dictionary mapping mode names to mode IDs for this protocol.
        
        Returns:
            Dictionary with mode names as keys and mode IDs as values.
            Example: {"MANUAL": 0x01, "RAINBOW": 0x04}
        """
        pass

