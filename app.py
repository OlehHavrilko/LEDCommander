"""
LED COMMANDER v3.0 - Professional RGB LED Control Application
Modern desktop interface with clean architecture and advanced BLE management.

Architecture: MVVM + Services Pattern
- UI Layer (views.py): Modern dashboard interface
- Business Logic (ble_controller.py): BLE communication and effects
- Data Layer (services.py): Configuration, logging, persistence
- Models (models.py): Domain entities and value objects
- Components (components.py): Reusable UI components
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services import ConfigService, LoggerService as logger
from ui import DashboardView, run_modern_ui
from ble_controller import BleApplicationBridge
from models import Color, ColorMode, DeviceStatus


class Application:
    """Main application controller."""
    
    def __init__(self):
        """Initialize application."""
        logger.separator("LED COMMANDER v3.0 - Initialization (ELK-BLEDOM UI)")
        
        # Initialize services
        self.bridge = BleApplicationBridge()
        self.ui: DashboardView = None
        
        logger.info("Configuration loaded")
    
    def run(self):
        """Run the application."""
        try:
            # Create and show UI
            self.ui = DashboardView()
            
            # Set up event handlers for color/mode/brightness/speed
            self.ui.controller.on_color_changed = self._handle_color_change
            self.ui.controller.on_mode_changed = self._handle_mode_change
            self.ui.controller.on_brightness_changed = self._handle_brightness_change
            self.ui.controller.on_speed_changed = self._handle_speed_change
            
            # Initialize BLE bridge with status callback
            self.bridge.on_status_change = self._handle_device_status_update
            self.bridge.initialize()
            
            # Start periodic status updates
            self._schedule_status_update()
            
            logger.success("Application started successfully")
            
            # Run UI main loop
            self.ui.mainloop()
            
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise
        finally:
            self.shutdown()
    
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
        if self.ui:
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
        if self.ui and self.ui.winfo_exists():
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


def main():
    """Entry point."""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
