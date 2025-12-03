# Copilot / AI Agent Instructions for LED COMMANDER v3.0

**Architecture**: MVVM + Services Pattern | **Status**: Production Ready

## 1. Quick Start for AI Agents

### Project Structure
```
ledcontrol/
├── app.py                    # Main entry point, orchestrates components
├── ui.py                     # Modern dashboard (MVVM view layer)
├── ble_controller.py         # BLE communication & effects engine
├── models.py                 # Domain entities (Color, ColorMode, etc.)
├── services.py               # ConfigService, LoggerService
├── components.py             # Reusable UI widget library
├── main.py                   # Legacy entry point (deprecated)
├── .github/
│   ├── AI_AGENT_GUIDE.md    # Comprehensive architecture docs
│   └── copilot-instructions.md  # This file
└── led_config.json           # Auto-generated config
```

### Run Application
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Run modern UI (v3.0)
python app.py

# Run legacy UI (v2.1)
python main.py
```

### Build Executable
```powershell
pyinstaller --onefile main.spec
# Output: dist/main.exe
```

## 2. Architecture Layers (MVVM + Services)

### Layer Breakdown

| Layer | Module | Purpose | When to Edit |
|-------|--------|---------|-------------|
| **Presentation** | `ui.py` | Dashboard, event handling | Add UI features, change layout |
| **Business** | `ble_controller.py` | BLE communication, effect modes | Add effects, fix BLE issues |
| **Data** | `services.py` | Config persistence, logging | Change config format, logs |
| **Models** | `models.py` | Value objects (Color, Status) | Extend domain concepts |
| **Components** | `components.py` | Reusable widgets | Create new UI components |
| **Bootstrap** | `app.py` | Application startup | Integration logic |

### Data Flow
```
UI User Action
    ↓
ModernUIController Event
    ↓
BleApplicationBridge
    ↓
BleDeviceController (async thread)
    ↓
BLE Device
    ↓
[Response]
    ↓
DeviceStatus Update
    ↓
DashboardView.update_device_status()
```

## 3. Key Components & Patterns

### 3.1 Models (Immutable Value Objects)
```python
from models import Color, ColorMode, DeviceStatus

# Color with validation
color = Color(255, 128, 0)
hex_str = color.to_hex()  # "#FF8000"
dimmed = color.apply_brightness(0.5)  # New Color(127, 64, 0)

# Color modes
ColorMode.MANUAL | ColorMode.CPU | ColorMode.BREATH | ColorMode.RAINBOW

# Device status (real-time state)
status = DeviceStatus(
    is_connected=True,
    device_name="LED Controller",
    signal_strength=-65,
    current_mode=ColorMode.CPU,
    current_color=Color(255, 0, 0)
)
```

### 3.2 BLE Controller (Async Background Thread)
```python
from ble_controller import BleDeviceController
from models import DeviceConfig

config = DeviceConfig(
    target_mac="FF:FF:10:69:5B:2A",
    write_char_uuid="0000fff3-0000-1000-8000-00805f9b34fb"
)

controller = BleDeviceController(
    device_config=config,
    on_status_change=lambda status: print(status),
    on_color_received=lambda color: print(color)
)

controller.start()
controller.set_mode(ColorMode.CPU)
controller.set_color(Color(255, 0, 0))
controller.set_brightness(0.8)
controller.stop()
```

**Important**: 
- Runs in separate asyncio event loop in daemon thread
- Never call UI methods from BLE thread
- Status updates marshalled to main thread

### 3.3 Services (Static Singletons)
```python
from services import ConfigService, LoggerService as logger

# Config
config = ConfigService.load_config()
prefs = ConfigService.get_preferences()
ConfigService.save_preferences(prefs)

# Logging
logger.info("Application started")
logger.debug("Detailed diagnostic")
logger.warning("Something unexpected")
logger.error("Error occurred")
logger.success("Operation complete")
logger.separator("SECTION TITLE")
```

### 3.4 UI Components (Reusable Library)
```python
from components import StatusBadge, ColorPreview, SliderGroup, EffectCard

# Status indicator
badge = StatusBadge(parent, status="connected")
badge.set_status("connecting")

# Color preview with hex/RGB
preview = ColorPreview(parent, color=(255, 0, 128))

# RGB slider with live display
slider = SliderGroup(parent, "R", "#FF4444", on_change=lambda v: ...)
value = slider.get()

# Effect mode card
card = EffectCard(
    parent,
    title="CPU MONITOR",
    description="Color follows CPU",
    icon="📊",
    on_click=lambda: set_mode(...),
    selected=True
)
```

### 3.5 Modern UI (Dashboard View)
```python
from ui import DashboardView

app = DashboardView()

# Wire event handlers
app.controller.on_color_changed = lambda color: bridge.set_color(color)
app.controller.on_mode_changed = lambda mode: bridge.set_mode(mode)
app.controller.on_brightness_changed = lambda b: bridge.set_brightness(b)

# Update display
from models import DeviceStatus
app.update_device_status(DeviceStatus(...))

app.mainloop()
```

## 4. Adding New Features

### 4.1 Add New Effect Mode

**1. Extend ColorMode enum** (`models.py`)
```python
class ColorMode(str, Enum):
    MANUAL = "MANUAL"
    CPU = "CPU"
    BREATH = "BREATH"
    RAINBOW = "RAINBOW"
    PULSE = "PULSE"  # NEW
```

**2. Implement effect logic** (`ble_controller.py`)
```python
async def _execute_mode(self):
    # ... existing code ...
    elif self.current_mode == ColorMode.PULSE:
        await self._execute_pulse_mode()

async def _execute_pulse_mode(self):
    """Red pulsing effect."""
    while self.current_mode == ColorMode.PULSE and self.is_running:
        for intensity in [0.3, 0.6, 1.0, 0.6]:
            color = Color(int(255 * intensity), 0, 0)
            await self._send_color(color)
            await asyncio.sleep(0.3)
```

**3. Add UI card** (`ui.py`)
```python
self.card_pulse = EffectCard(
    effects_frame,
    "PULSE",
    "Red pulsing effect",
    "💥",
    on_click=lambda: self._set_mode(ColorMode.PULSE)
)
self.card_pulse.pack(fill="x", pady=5)
```

### 4.2 Add New Component

Inherit from `ctk.CTkFrame` and follow naming convention:
```python
# components.py
class CustomWidget(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._create_widgets()
    
    def _create_widgets(self):
        # Build UI
        pass
    
    def update_state(self, data):
        # Handle updates
        pass
```

### 4.3 Change Device Configuration

Edit `led_config.json`:
```json
{
  "device": {
    "target_mac": "AA:BB:CC:DD:EE:FF",
    "write_char_uuid": "0000fff3-0000-1000-8000-00805f9b34fb"
  }
}
```

Or programmatically:
```python
from services import ConfigService
config = ConfigService.load_config()
config["device"]["target_mac"] = "NEW_MAC"
ConfigService.save_config(config)
```

## 5. Common Tasks

### Task: Fix BLE Connection Issue
1. Check MAC in `led_config.json`
2. Verify UUID matches device (use nRF Connect app)
3. Enable Bluetooth in Windows Settings
4. Check logs: `led_control.log`
5. Try force reconnect button in UI

### Task: Customize Colors
1. Edit `ColorPreset.default_presets()` in `models.py`
2. Add to `presets` list or `custom_presets` in config

### Task: Add Keyboard Shortcut
```python
# ui.py, in DashboardView.__init__()
self.bind("<Shift-R>", lambda e: self._set_mode(ColorMode.RAINBOW))
```

### Task: Change Logging Level
```python
# services.py
# Uncomment for DEBUG level
os.environ['LOG_LEVEL'] = 'DEBUG'
```

## 6. Important Constraints & Patterns

### ⚠️ Threading Rules
- **NEVER** call UI methods from BLE thread
- Use `self.after(0, lambda: ...)` to marshal to main thread
- Callbacks execute in BLE thread: keep them fast

### ⚠️ Color Validation
```python
# Always clamp RGB to 0-255
color = Color(300, -50, 128)  # Auto-clamped to (255, 0, 128)
```

### ⚠️ Async/Await Pattern
```python
# All BLE operations must be async
async def _send_color(self, color: Color):
    if self.client and self.client.is_connected:
        await self.client.write_gatt_char(...)

# Use await, not .run_until_complete()
```

### ✅ Error Handling Best Practices
```python
try:
    await self._send_color(color)
except Exception as e:
    logger.error(f"Send failed: {e}")
    # Always continue loop, don't exit
    await asyncio.sleep(1)
```

## 7. Testing & Debugging

### Run with DEBUG logging
```python
# In services.py or at runtime
import os
os.environ['DEBUG'] = '1'
```

### Mock BLE for testing
```python
import os
os.environ['TEST_MODE'] = '1'

# BLE calls will be skipped/mocked
```

### Inspect device configuration
```python
from services import ConfigService
config = ConfigService.load_config()
print(json.dumps(config, indent=2))
```

## 8. File References

- **Config template**: `ConfigService.DEFAULT_CONFIG` (services.py)
- **Logging**: Check `led_control.log` (auto-rotates at 5MB)
- **Device payload format**: `BleDeviceController._send_color()` (ble_controller.py)
- **UI layouts**: `DashboardView._create_*` methods (ui.py)

## 9. Version History

| Version | Changes | Entry Point |
|---------|---------|------------|
| **v3.0** | MVVM architecture, modern UI, component library | `app.py` |
| v2.1 | Config system, logging, Rainbow mode | `main.py` |
| v1.0 | Basic sliders and modes | N/A |

---

**For comprehensive documentation**: See `.github/AI_AGENT_GUIDE.md`

**For user documentation**: See `README.md`

