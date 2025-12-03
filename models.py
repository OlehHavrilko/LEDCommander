"""
Data models and domain logic for LED Control application.
Represents core business entities and their state management.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ColorMode(str, Enum):
    """Enum for available color modes/effects."""
    MANUAL = "MANUAL"
    CPU = "CPU"
    BREATH = "BREATH"
    RAINBOW = "RAINBOW"


@dataclass
class Color:
    """Immutable RGB color representation."""
    r: int = 0
    g: int = 0
    b: int = 0
    
    def __post_init__(self):
        """Validate and clamp RGB values to 0-255."""
        self.r = max(0, min(255, int(self.r)))
        self.g = max(0, min(255, int(self.g)))
        self.b = max(0, min(255, int(self.b)))
    
    def to_hex(self) -> str:
        """Convert to hex string format #RRGGBB."""
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"
    
    @staticmethod
    def from_hex(hex_str: str) -> 'Color':
        """Parse hex string (#RRGGBB or RRGGBB) to Color."""
        hex_str = hex_str.lstrip('#')
        if len(hex_str) != 6:
            raise ValueError(f"Invalid hex color: {hex_str}")
        try:
            return Color(
                r=int(hex_str[0:2], 16),
                g=int(hex_str[2:4], 16),
                b=int(hex_str[4:6], 16)
            )
        except ValueError as e:
            raise ValueError(f"Failed to parse hex color: {hex_str}") from e
    
    def apply_brightness(self, brightness: float) -> 'Color':
        """Apply brightness multiplier (0.0 - 1.0) and return new Color."""
        brightness = max(0.0, min(1.0, brightness))
        return Color(
            r=int(self.r * brightness),
            g=int(self.g * brightness),
            b=int(self.b * brightness)
        )
    
    def to_tuple(self) -> Tuple[int, int, int]:
        """Return (r, g, b) tuple."""
        return (self.r, self.g, self.b)
    
    def to_dict(self) -> Dict[str, int]:
        """Return dict representation for JSON serialization."""
        return {"r": self.r, "g": self.g, "b": self.b}
    
    @staticmethod
    def from_dict(data: Dict) -> 'Color':
        """Create Color from dict representation."""
        return Color(r=data.get("r", 0), g=data.get("g", 0), b=data.get("b", 0))


@dataclass
class DeviceConfig:
    """Configuration for BLE device connection."""
    target_mac: str
    write_char_uuid: str
    device_name: str = "Unknown LED Device"
    
    def to_dict(self) -> Dict:
        """Serialize to dict."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict) -> 'DeviceConfig':
        """Deserialize from dict."""
        return DeviceConfig(
            target_mac=data.get("target_mac", ""),
            write_char_uuid=data.get("write_char_uuid", ""),
            device_name=data.get("device_name", "Unknown LED Device")
        )


@dataclass
class AppPreferences:
    """User preferences and app settings."""
    brightness: float = 1.0
    last_color: Color = field(default_factory=lambda: Color(255, 255, 255))
    last_mode: ColorMode = ColorMode.MANUAL
    theme: str = "dark"
    auto_reconnect: bool = True
    reconnect_interval: float = 5.0
    default_speed: int = 16  # 0..255, used for effect speed
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Validate preferences values."""
        self.brightness = max(0.0, min(1.0, float(self.brightness)))
        self.reconnect_interval = max(1.0, float(self.reconnect_interval))
        # Clamp speed
        try:
            self.default_speed = max(0, min(255, int(self.default_speed)))
        except Exception:
            self.default_speed = 16
    
    def to_dict(self) -> Dict:
        """Serialize to dict for JSON storage."""
        return {
            "brightness": self.brightness,
            "last_color": self.last_color.to_dict(),
            "last_mode": self.last_mode.value,
            "theme": self.theme,
            "auto_reconnect": self.auto_reconnect,
            "reconnect_interval": self.reconnect_interval,
            "default_speed": int(self.default_speed),
            "last_updated": self.last_updated
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'AppPreferences':
        """Deserialize from dict."""
        return AppPreferences(
            brightness=data.get("brightness", 1.0),
            last_color=Color.from_dict(data.get("last_color", {})),
            last_mode=ColorMode(data.get("last_mode", "MANUAL")),
            theme=data.get("theme", "dark"),
            auto_reconnect=data.get("auto_reconnect", True),
            reconnect_interval=data.get("reconnect_interval", 5.0),
            default_speed=data.get("default_speed", 16),
            last_updated=data.get("last_updated", datetime.now().isoformat())
        )


@dataclass
class ColorPreset:
    """Pre-defined color preset."""
    name: str
    color: Color
    description: str = ""
    
    @staticmethod
    def default_presets() -> List['ColorPreset']:
        """Return standard color palette."""
        return [
            ColorPreset("Red", Color(255, 0, 0), "Pure red"),
            ColorPreset("Green", Color(0, 255, 0), "Pure green"),
            ColorPreset("Blue", Color(0, 0, 255), "Pure blue"),
            ColorPreset("White", Color(255, 255, 255), "Full brightness white"),
            ColorPreset("Cyan", Color(0, 255, 255), "Cyan"),
            ColorPreset("Magenta", Color(255, 0, 255), "Magenta"),
            ColorPreset("Yellow", Color(255, 255, 0), "Yellow"),
            ColorPreset("Purple", Color(128, 0, 128), "Dark purple"),
            ColorPreset("Orange", Color(255, 165, 0), "Orange"),
        ]


@dataclass
class DeviceStatus:
    """Current device connection and state information."""
    is_connected: bool = False
    device_name: str = "Not Connected"
    signal_strength: int = 0  # RSSI in dBm, typically -100 to -30
    current_mode: ColorMode = ColorMode.MANUAL
    current_color: Color = field(default_factory=Color)
    last_sync: Optional[datetime] = None
    error_message: Optional[str] = None
    cpu_usage: Optional[float] = None  # For CPU monitor mode
    
    def is_healthy(self) -> bool:
        """Check if device connection is healthy."""
        return self.is_connected and (self.error_message is None)
