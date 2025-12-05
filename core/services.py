"""
Service layer for data persistence, configuration management, and logging.
Implements repository pattern and provides abstraction over storage and I/O.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from core.models import DeviceConfig, AppPreferences, ColorPreset, Color


class ConfigService:
    """Manages application configuration persistence."""
    
    CONFIG_FILE = "led_config.json"
    LOG_FILE = "led_control.log"
    
    # Default configuration template
    DEFAULT_CONFIG = {
        "device": {
            "target_mac": "FF:FF:10:69:5B:2A",
            "write_char_uuid": "0000fff3-0000-1000-8000-00805f9b34fb",
            "device_name": "LED Controller",
            "protocol": None  # None = auto-detect, or specify "elk_bledom", "triones", etc.
        },
        "preferences": {
            "brightness": 1.0,
            "last_color": {"r": 255, "g": 255, "b": 255},
            "last_mode": "MANUAL",
            "theme": "dark",
            "auto_reconnect": True,
            "reconnect_interval": 5.0,
            "default_speed": 16
        },
        "custom_presets": []
    }
    
    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """Load configuration from file or return default."""
        try:
            if os.path.exists(cls.CONFIG_FILE):
                with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return cls._merge_defaults(config)
            return cls.DEFAULT_CONFIG.copy()
        except Exception as e:
            LoggerService.error(f"Failed to load config: {e}")
            return cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def save_config(cls, config: Dict[str, Any]) -> bool:
        """Save configuration to file."""
        try:
            with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            LoggerService.info("Config saved successfully")
            return True
        except Exception as e:
            LoggerService.error(f"Failed to save config: {e}")
            return False
    
    @classmethod
    def get_device_config(cls) -> DeviceConfig:
        """Get device configuration."""
        config = cls.load_config()
        device_data = config.get("device", {})
        return DeviceConfig.from_dict(device_data)
    
    @classmethod
    def get_preferences(cls) -> AppPreferences:
        """Get application preferences."""
        config = cls.load_config()
        prefs_data = config.get("preferences", {})
        return AppPreferences.from_dict(prefs_data)
    
    @classmethod
    def save_preferences(cls, preferences: AppPreferences) -> bool:
        """Save application preferences."""
        config = cls.load_config()
        config["preferences"] = preferences.to_dict()
        return cls.save_config(config)
    
    @classmethod
    def get_custom_presets(cls) -> list:
        """Get saved custom color presets."""
        config = cls.load_config()
        presets_data = config.get("custom_presets", [])
        return [ColorPreset(**p) for p in presets_data]
    
    @classmethod
    def save_custom_preset(cls, preset: ColorPreset) -> bool:
        """Add custom color preset to saved list."""
        config = cls.load_config()
        config["custom_presets"].append({
            "name": preset.name,
            "color": preset.color.to_dict(),
            "description": preset.description
        })
        return cls.save_config(config)
    
    @classmethod
    def _merge_defaults(cls, config: Dict) -> Dict:
        """Recursively merge config with defaults."""
        result = cls.DEFAULT_CONFIG.copy()
        for key, value in config.items():
            if isinstance(value, dict) and key in result:
                result[key] = {**result[key], **value}
            else:
                result[key] = value
        return result


class LoggerService:
    """Centralized logging service with file and console output."""
    
    LOG_FILE = "led_control.log"
    MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
    
    @classmethod
    def _get_log_level_prefix(cls, level: str) -> str:
        """Get prefix for log level."""
        prefixes = {
            "INFO": "ℹ️  ",
            "DEBUG": "🐛 ",
            "WARNING": "⚠️  ",
            "ERROR": "❌ ",
            "SUCCESS": "✅ "
        }
        return prefixes.get(level, "")
    
    @classmethod
    def _format_message(cls, level: str, message: str) -> str:
        """Format log message with timestamp and level."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = cls._get_log_level_prefix(level)
        return f"[{timestamp}] {prefix}[{level}] {message}"
    
    @classmethod
    def _rotate_log_if_needed(cls):
        """Rotate log file if it exceeds max size."""
        if os.path.exists(cls.LOG_FILE):
            if os.path.getsize(cls.LOG_FILE) > cls.MAX_LOG_SIZE:
                backup_name = f"{cls.LOG_FILE}.backup"
                if os.path.exists(backup_name):
                    os.remove(backup_name)
                os.rename(cls.LOG_FILE, backup_name)
    
    @classmethod
    def _write_to_file(cls, message: str):
        """Write message to log file."""
        try:
            cls._rotate_log_if_needed()
            with open(cls.LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(message + "\n")
        except Exception as e:
            print(f"Failed to write to log file: {e}")
    
    @classmethod
    def info(cls, message: str):
        """Log info message."""
        formatted = cls._format_message("INFO", message)
        print(formatted)
        cls._write_to_file(formatted)
    
    @classmethod
    def debug(cls, message: str):
        """Log debug message."""
        formatted = cls._format_message("DEBUG", message)
        print(formatted)
        cls._write_to_file(formatted)
    
    @classmethod
    def warning(cls, message: str):
        """Log warning message."""
        formatted = cls._format_message("WARNING", message)
        print(formatted)
        cls._write_to_file(formatted)
    
    @classmethod
    def error(cls, message: str):
        """Log error message."""
        formatted = cls._format_message("ERROR", message)
        print(formatted)
        cls._write_to_file(formatted)
    
    @classmethod
    def success(cls, message: str):
        """Log success message."""
        formatted = cls._format_message("SUCCESS", message)
        print(formatted)
        cls._write_to_file(formatted)
    
    @classmethod
    def separator(cls, title: str = ""):
        """Log separator line."""
        line = "=" * 60
        if title:
            cls.info(f"{line} {title} {line}")
        else:
            cls.info(line)


# Global logger instance
logger = LoggerService()

