"""
Device driver factory with automatic protocol detection (fingerprinting).
Selects appropriate driver based on configuration or device characteristics.
"""

from typing import Optional, Dict, Type
from bleak import BLEDevice

from core.interfaces import AbstractLedDevice
from core.drivers.elk_bledom import ElkBledomDriver
from core.drivers.triones import TrionesDriver
from core.drivers.magichome import MagicHomeDriver
from core.drivers.tuya import TuyaDriver


# Registry of available drivers
_DRIVER_REGISTRY: Dict[str, Type[AbstractLedDevice]] = {
    "elk_bledom": ElkBledomDriver,
    "elk": ElkBledomDriver,  # Alias
    "bledom": ElkBledomDriver,  # Alias
    "triones": TrionesDriver,
    "magichome": MagicHomeDriver,
    "magic_home": MagicHomeDriver,  # Alias
    "magic": MagicHomeDriver,  # Alias
    "tuya": TuyaDriver,
}

# Protocol detection order (most specific first)
_DETECTION_ORDER = [
    TrionesDriver,      # Check Triones first (more specific UUID patterns)
    MagicHomeDriver,    # Then MagicHome
    TuyaDriver,         # Then Tuya
    ElkBledomDriver,    # ELK-BLEDOM as fallback (most common)
]


class DeviceFactory:
    """
    Factory for creating LED device drivers.
    
    Supports:
    1. Explicit protocol selection via configuration
    2. Automatic detection (fingerprinting) based on device characteristics
    """
    
    @staticmethod
    def create_driver(
        protocol_type: Optional[str] = None,
        device: Optional[BLEDevice] = None
    ) -> AbstractLedDevice:
        """
        Create appropriate driver instance.
        
        Args:
            protocol_type: Explicit protocol name from config (e.g., "elk_bledom").
                          If None, attempts automatic detection.
            device: BLEDevice instance for fingerprinting. Required if protocol_type is None.
            
        Returns:
            AbstractLedDevice instance.
            
        Raises:
            ValueError: If protocol_type is invalid or device cannot be detected.
        """
        # Explicit protocol selection
        if protocol_type:
            protocol_lower = protocol_type.lower().strip()
            driver_class = _DRIVER_REGISTRY.get(protocol_lower)
            
            if driver_class:
                return driver_class()
            else:
                available = ", ".join(_DRIVER_REGISTRY.keys())
                raise ValueError(
                    f"Unknown protocol: {protocol_type}. "
                    f"Available: {available}"
                )
        
        # Automatic detection (fingerprinting)
        if device is None:
            raise ValueError(
                "Either protocol_type or device must be provided for driver creation"
            )
        
        return DeviceFactory._detect_driver(device)
    
    @staticmethod
    def _detect_driver(device: BLEDevice) -> AbstractLedDevice:
        """
        Automatically detect device protocol using fingerprinting.
        
        Detection strategy:
        1. Check device name patterns
        2. Check advertised service UUIDs
        3. Try each driver's can_handle_device() method
        
        Args:
            device: BLEDevice instance to analyze.
            
        Returns:
            AbstractLedDevice instance for detected protocol.
            
        Raises:
            ValueError: If no compatible driver found.
        """
        device_name = device.name
        service_uuids = []
        
        # Extract service UUIDs from device metadata
        if hasattr(device, 'metadata') and device.metadata:
            services = device.metadata.get('uuids', [])
            service_uuids = [str(uuid) for uuid in services]
        
        # Try each driver in detection order
        for driver_class in _DETECTION_ORDER:
            if driver_class.can_handle_device(device_name, service_uuids):
                return driver_class()
        
        # Fallback: if device name contains common LED keywords, default to ELK-BLEDOM
        if device_name:
            name_upper = device_name.upper()
            if any(keyword in name_upper for keyword in ["LED", "RGB", "CTRL", "LIGHT"]):
                return ElkBledomDriver()
        
        raise ValueError(
            f"Could not detect protocol for device: {device_name or device.address}. "
            f"Please specify protocol_type in configuration."
        )
    
    @staticmethod
    def register_driver(protocol_name: str, driver_class: Type[AbstractLedDevice]) -> None:
        """
        Register a new driver class for a protocol.
        
        Args:
            protocol_name: Protocol identifier (e.g., "triones", "magichome")
            driver_class: Driver class implementing AbstractLedDevice
        """
        _DRIVER_REGISTRY[protocol_name.lower()] = driver_class
        if driver_class not in _DETECTION_ORDER:
            _DETECTION_ORDER.append(driver_class)
    
    @staticmethod
    def get_available_protocols() -> list:
        """Get list of available protocol names."""
        return list(_DRIVER_REGISTRY.keys())
    
    @staticmethod
    def is_protocol_supported(protocol_name: str) -> bool:
        """Check if a protocol is supported."""
        return protocol_name.lower() in _DRIVER_REGISTRY

