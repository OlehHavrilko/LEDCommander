"""
LED COMMANDER v3.0 - Entry point.
Minimal startup script that initializes config, creates window, and runs mainloop.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.services import LoggerService as logger
from ui.main_window import DashboardView
from ui.viewmodels import Application


def main():
    """Entry point - initialize and run application."""
    try:
        logger.separator("LED COMMANDER v3.0 - Starting")
        
        # Create UI window
        ui = DashboardView()
        
        # Create ViewModel (Application)
        app = Application()
        app.run(ui)
        
        # Set up window close handler
        def on_closing():
            app.shutdown()
            ui.destroy()
        
        ui.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Run UI main loop
        ui.mainloop()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
