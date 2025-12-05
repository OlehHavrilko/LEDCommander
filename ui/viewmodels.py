"""
LED COMMANDER v3.0 - ViewModel layer.
Bridge between UI and Core business logic.
Handles event processing and connects UI actions to BLE controller.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.services import ConfigService, LoggerService as logger
from core.controller import BleApplicationBridge
from core.models import Color, ColorMode, DeviceStatus


class Application:
    """Main application controller - ViewModel layer."""
    
    def __init__(self):
        """Initialize application."""
        logger.separator("LED COMMANDER v3.0 - Initialization")
        
        # Initialize services
        self.bridge = BleApplicationBridge()
        self.ui = None  # Will be set by main.py
        
        logger.info("Configuration loaded")
    
    def run(self, ui_window):
        """Run the application with UI window."""
        try:
            # Store UI reference
            self.ui = ui_window
            
            # Set up event handlers for color/mode/brightness/speed
            if hasattr(ui_window, 'controller'):
                ui_window.controller.on_color_changed = self._handle_color_change
                ui_window.controller.on_mode_changed = self._handle_mode_change
                ui_window.controller.on_brightness_changed = self._handle_brightness_change
                ui_window.controller.on_speed_changed = self._handle_speed_change
            
            # Initialize BLE bridge with status callback
            self.bridge.on_status_change = self._handle_device_status_update
            self.bridge.initialize()
            
            # Start periodic status updates
            self._schedule_status_update()
            
            logger.success("Application started successfully")
            
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise
    
    def _handle_color_change(self, color: Color):
        """Handle color change from UI."""
        self.bridge.set_color(color)
        logger.debug(f"Color set: {color.to_hex()}")
    
    def _handle_mode_change(self, mode: ColorMode):
        """Handle mode change from UI."""
        self.bridge.set_mode(mode)
        logger.debug(f"Mode changed: {mode.value}")
    
    def _handle_brightness_change(self, brightness: float):
        """Handle brightness change from UI."""
        self.bridge.set_brightness(brightness)
        logger.debug(f"Brightness set: {brightness * 100:.0f}%")
    
    def _handle_speed_change(self, speed: int):
        """Handle speed change from UI."""
        self.bridge.set_speed(speed)
        logger.debug(f"Speed set: {speed}")
    
    def _handle_device_status_update(self, status: DeviceStatus):
        """Handle device status update."""
        if self.ui and hasattr(self.ui, 'update_device_status'):
            self.ui.update_device_status(status)
    
    def _schedule_status_update(self):
        """Schedule periodic status updates from BLE controller."""
        if self.ui and self.bridge and hasattr(self.bridge, 'controller'):
            try:
                status = self.bridge.controller.status
                self._handle_device_status_update(status)
            except Exception as e:
                logger.debug(f"Status update failed: {e}")
        
        # Schedule next update in 1 second
        if self.ui and hasattr(self.ui, 'winfo_exists') and self.ui.winfo_exists():
            self.ui.after(1000, self._schedule_status_update)
    
    def shutdown(self):
        """Shutdown application cleanly."""
        logger.info("Shutting down...")
        try:
            self.bridge.save_preferences()
            self.bridge.shutdown()
        except Exception as e:
            logger.warning(f"Shutdown error: {e}")
        logger.separator("Application terminated")

