# LED COMMANDER v3.0 - AI Agent Implementation Guide

**Version**: 3.0  
**Last Updated**: December 4, 2025  
**Status**: Production Ready + Deployed (EXE built)  
**Target Audience**: AI coding agents, senior developers

## 1. Architecture Overview

### Design Pattern: MVVM + Services + Repository

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Entry Point (app.py)          │
│                  Orchestrates components & events            │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼──────┐  ┌──▼────────┐ ┌─▼────────────┐
    │ UI Layer  │  │ BLE Layer │ │ Service Layer│
    │ (ui.py)   │  │ (ble_...) │ │ (services.py)│
    └────┬──────┘  └──┬────────┘ └─┬────────────┘
         │            │            │
    ┌────▼────────────▼────────────▼──────────┐
    │  Data Models (models.py)                 │
    │  - Color, ColorMode, DeviceStatus       │
    │  - AppPreferences, DeviceConfig         │
    │  - ColorPreset, DeviceStatus            │
    └──────────────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │ Component Library (components.py)      │
    │ - StatusBadge, ColorPreview            │
    │ - SliderGroup, EffectCard              │
    │ - ToggleButton, StatPanel              │
    │ - DeviceDiscoveryList                  │
    └───────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Module | Purpose | Key Classes |
|-------|--------|---------|------------|
| **Presentation** | `ui.py` | Modern dashboard UI, event handling | `DashboardView`, `ModernUIController` |
| **Business Logic** | `ble_controller.py` | BLE communication, effect modes | `BleDeviceController`, `BleApplicationBridge` |
| **Data Persistence** | `services.py` | Config/log management, storage | `ConfigService`, `LoggerService` |
| **Models** | `models.py` | Domain entities, value objects | `Color`, `ColorMode`, `DeviceStatus` |
| **Components** | `components.py` | Reusable UI widgets | `StatusBadge`, `EffectCard`, `SliderGroup` |
| **Bootstrap** | `app.py` | Application initialization | `Application` |

---

## 2. Core Components

### 2.1 Data Models (`models.py`)

**Purpose**: Immutable value objects and data containers representing domain concepts.

#### Color
```python
Color(r: int, g: int, b: int)
Methods:
  - to_hex() → str              # "#RRGGBB"
  - from_hex(str) → Color       # Parse hex string
  - apply_brightness(float) → Color  # Scale RGB
  - to_tuple() → (int, int, int)
  - to_dict() → {r, g, b}
```

**Usage Pattern**:
```python
color = Color(255, 0, 128)
hex_val = color.to_hex()  # "#FF0080"
dimmed = color.apply_brightness(0.5)  # Halve brightness
```

#### ColorMode (Enum)
```python
ColorMode.MANUAL      # Direct color control
ColorMode.CPU         # CPU load → color
ColorMode.BREATH      # Pulsing animation
ColorMode.RAINBOW     # Spectrum cycle
```

#### DeviceStatus
Real-time device state container:
```python
@dataclass
class DeviceStatus:
    is_connected: bool
    device_name: str
    signal_strength: int       # RSSI in dBm
    current_mode: ColorMode
    current_color: Color
    error_message: Optional[str]
    cpu_usage: Optional[float]
```

#### AppPreferences
User settings container:
```python
@dataclass
class AppPreferences:
    brightness: float          # 0.0 - 1.0
    last_color: Color
    last_mode: ColorMode
    theme: str                 # "dark" or "light"
    auto_reconnect: bool
    reconnect_interval: float  # seconds
```

### 2.2 Service Layer (`services.py`)

**Purpose**: Abstract I/O operations and provide cross-cutting concerns.

#### ConfigService
```python
ConfigService.load_config() → Dict
ConfigService.save_config(config: Dict) → bool
ConfigService.get_device_config() → DeviceConfig
ConfigService.get_preferences() → AppPreferences
ConfigService.save_preferences(prefs) → bool
ConfigService.get_custom_presets() → List[ColorPreset]
ConfigService.save_custom_preset(preset) → bool
```

**File Structure**: `led_config.json`
```json
{
  "device": {
    "target_mac": "FF:FF:10:69:5B:2A",
    "write_char_uuid": "0000fff3-0000-1000-8000-00805f9b34fb",
    "device_name": "LED Controller"
  },
  "preferences": {
    "brightness": 1.0,
    "last_color": {"r": 255, "g": 255, "b": 255},
    "last_mode": "MANUAL",
    "theme": "dark"
  },
  "custom_presets": []
}
```

#### LoggerService
```python
LoggerService.info(msg: str)      # ℹ️  [INFO]
LoggerService.debug(msg: str)     # 🐛 [DEBUG]
LoggerService.warning(msg: str)   # ⚠️  [WARNING]
LoggerService.error(msg: str)     # ❌ [ERROR]
LoggerService.success(msg: str)   # ✅ [SUCCESS]
LoggerService.separator(title="") # === TITLE ===
```

**Output**: Console + `led_control.log` (auto-rotation at 5MB)

### 2.3 Component Library (`components.py`)

**Purpose**: Reusable, themeable UI components for consistency.

#### StatusBadge
Visual status indicator with color-coded states.
```python
badge = StatusBadge(parent, status="connected")
badge.set_status("connected")     # ● ONLINE (green)
badge.set_status("connecting")    # ⟳ CONNECTING (orange)
badge.set_status("disconnected")  # ○ OFFLINE (red)
badge.set_status("error")         # ⚠ ERROR (red)
```

#### ColorPreview
Shows color with hex/RGB values.
```python
preview = ColorPreview(parent, color=(255, 0, 128))
preview.set_color((100, 200, 50))
```

#### SliderGroup
RGB slider with label and live value display.
```python
slider = SliderGroup(
    parent, 
    label="R",
    color="#FF4444",
    on_change=lambda v: print(f"Value: {v}")
)
value = slider.get()  # 0-255
slider.set(128)
```

#### EffectCard
Clickable card for mode/effect selection.
```python
card = EffectCard(
    parent,
    title="NEON BREATH",
    description="Smooth pulsing animation",
    icon="💜",
    on_click=lambda: set_mode(ColorMode.BREATH),
    selected=False
)
card.set_selected(True)
```

#### ToggleButton
Maintains on/off state.
```python
toggle = ToggleButton(
    parent,
    text_on="ENABLED",
    text_off="DISABLED",
    on_toggle=lambda state: print(f"Toggled: {state}")
)
toggle.set_on(True)
```

#### StatPanel
Displays key-value statistics.
```python
panel = StatPanel(parent, title="Connection Stats")
panel.set_stat("Status", "✓ Connected")
panel.set_stat("Mode", "CPU Monitor")
panel.set_stat("Signal", "-65 dBm")
```

#### DeviceDiscoveryList
Scrollable list of discovered BLE devices.
```python
device_list = DeviceDiscoveryList(
    parent,
    on_select=lambda name, mac: connect_device(mac)
)
device_list.add_device("LED Controller", "FF:FF:10:69:5B:2A", rssi=-65)
device_list.clear()
```

### 2.4 BLE Controller (`ble_controller.py`)

**Purpose**: Async BLE communication and effect mode execution.

#### BleDeviceController
```python
controller = BleDeviceController(
    device_config=DeviceConfig(...),
    on_status_change=lambda status: update_ui(status),
    on_color_received=lambda color: print(color)
)

controller.start()                    # Start background event loop
controller.set_mode(ColorMode.CPU)   # Change mode
controller.set_color(Color(255, 0, 0))  # Set color
controller.set_brightness(0.8)        # Set brightness
controller.stop()                     # Stop and cleanup
```

**Effect Modes**:
- **MANUAL**: Direct color control (uses `current_color`)
- **CPU**: Color based on CPU load (Cyan→Violet→Red)
- **BREATH**: Smooth pulsing animation (purple glow)
- **RAINBOW**: Full spectrum cycle

**Payload Format** (BLE write):
```
[0x7E, 0x07, 0x05, 0x03, R, G, B, 0x10, 0xEF]
```

#### BleApplicationBridge
```python
bridge = BleApplicationBridge()
bridge.initialize()
bridge.set_color(Color(255, 128, 0))
bridge.set_brightness(0.9)
bridge.set_mode(ColorMode.RAINBOW)
bridge.save_preferences()
bridge.shutdown()
```

### 2.5 UI Layer (`ui.py`)

**Purpose**: Modern dashboard interface with responsive layout.

#### ModernUIController
Event dispatcher for UI-to-business logic communication.
```python
controller = ModernUIController()
controller.on_color_changed = lambda color: ble.set_color(color)
controller.on_mode_changed = lambda mode: ble.set_mode(mode)
controller.on_brightness_changed = lambda b: ble.set_brightness(b)

# Emit events
controller.emit_color_change(Color(255, 0, 0))
```

#### DashboardView
Main application window inherits `ctk.CTk`.

**Layout Structure**:
```
┌─ Header (Status + Signal) ─────────────────────────────────┐
├───────────────────────────┬─ Right Panel (300px) ──────────┤
│                           │ Quick Presets                   │
│ Tabs:                     ├─────────────────────────────────┤
│ - 🎨 COLOR (sliders)     │ Status Panel                    │
│ - ✨ EFFECTS (cards)      │ - Connection Stats             │
│ - ⚙️ ADVANCED (settings) │                                │
│                           │                                │
└───────────────────────────┴────────────────────────────────┘
```

**Key Methods**:
```python
app = DashboardView()
app.update_device_status(status)  # Update UI with device info
app.on_closing()                  # Cleanup
```

### 2.6 Main Application (`app.py`)

**Purpose**: Bootstrap and orchestrate all components.

```python
class Application:
    def __init__(self):
        self.bridge = BleApplicationBridge()  # Services
        self.ui = None
    
    def run(self):
        self.ui = DashboardView()
        self.ui.controller.on_color_changed = self._handle_color_change
        self.bridge.initialize()
        self.ui.mainloop()
    
    def shutdown(self):
        self.bridge.save_preferences()
        self.bridge.shutdown()
```

**Execution Flow**:
1. Initialize services (config, logging)
2. Create BLE bridge and UI
3. Wire up event handlers
4. Start BLE background loop
5. Display UI main window
6. Handle window close → cleanup

---

## 3. Key Design Patterns

### 3.1 Event-Driven Communication
```python
# UI → Business Logic
controller.on_color_changed = lambda color: bridge.set_color(color)

# Business Logic → UI
bridge.on_ui_update = lambda status: ui.update_device_status(status)
```

### 3.2 Asyncio + Threading
- BLE runs in separate asyncio event loop in background thread
- All UI updates marshalled back to main thread via `after()`
- No blocking calls in main thread

```python
def _emit_status_change(self, message, status_type):
    # This runs in BLE thread, safe to call
    try:
        self.on_status_change(self.status)
    except Exception as e:
        logger.debug(f"Callback error: {e}")
```

### 3.3 Immutable Value Objects
```python
# Color is immutable
color1 = Color(255, 0, 128)
color2 = color1.apply_brightness(0.5)  # Returns new Color
# color1 unchanged

# Safe to use as dict keys, compare by value
colors_set = {color1, color2}
```

### 3.4 Service Locator Pattern
```python
# ConfigService and LoggerService are static/class methods
# No DI container needed for simple cases
config = ConfigService.load_config()
logger.info("Starting...")
```

---

## 4. Configuration & Customization

### 4.1 Adding New Effect Mode

**Step 1**: Add to ColorMode enum
```python
# models.py
class ColorMode(str, Enum):
    PULSE = "PULSE"
```

**Step 2**: Implement effect logic
```python
# ble_controller.py, in BleDeviceController._execute_mode()
elif self.current_mode == ColorMode.PULSE:
    await self._execute_pulse_mode()

async def _execute_pulse_mode(self):
    """Custom pulse effect."""
    for _ in range(10):
        await self._send_color(Color(255, 0, 0))
        await asyncio.sleep(0.5)
        await self._send_color(Color(0, 0, 0))
        await asyncio.sleep(0.5)
```

**Step 3**: Add UI card
```python
# ui.py, in _create_effects_tab()
self.card_pulse = EffectCard(
    effects_frame,
    "PULSE",
    "Red pulsing effect",
    "💥",
    on_click=lambda: self._set_mode(ColorMode.PULSE)
)
self.card_pulse.pack(fill="x", pady=5)
```

### 4.2 Changing Device Configuration

**Option 1**: Edit `led_config.json`
```json
{
  "device": {
    "target_mac": "AA:BB:CC:DD:EE:FF",
    "write_char_uuid": "0000fff3-0000-1000-8000-00805f9b34fb"
  }
}
```

**Option 2**: Programmatically
```python
from services import ConfigService
config = ConfigService.load_config()
config["device"]["target_mac"] = "AA:BB:CC:DD:EE:FF"
ConfigService.save_config(config)
```

### 4.3 Theme Customization

Modify `ColorScheme` enum in `components.py`:
```python
class ColorScheme(Enum):
    DARK = {
        "bg": "#1a1a1a",
        "accent": "#8a0000",
        # ... other colors
    }
```

---

## 5. Testing & Debugging

### 5.1 Unit Testing

```python
from models import Color

def test_color_hex_conversion():
    color = Color.from_hex("#FF0080")
    assert color.r == 255
    assert color.g == 0
    assert color.b == 128
    assert color.to_hex() == "#FF0080"

def test_brightness_application():
    color = Color(200, 200, 200)
    dimmed = color.apply_brightness(0.5)
    assert dimmed.r == 100
    assert dimmed.g == 100
    assert dimmed.b == 100
```

### 5.2 Logging Levels

```python
LoggerService.debug("Detailed diagnostic info")      # Development
LoggerService.info("Normal operational info")        # Standard
LoggerService.warning("Something unexpected")        # Caution
LoggerService.error("Error occurred: {details}")     # Problem
LoggerService.success("Operation completed")         # Confirmation
```

### 5.3 Mocking BLE for Testing

```python
# Set TEST_MODE to skip actual BLE
import os
os.environ['TEST_MODE'] = '1'

# Wrap BLE calls
if not os.environ.get('TEST_MODE'):
    device = await BleakScanner.find_device_by_address(...)
else:
    device = MockDevice()
```

---

## 6. Performance Considerations

### 6.1 Event Loop Efficiency
- Color updates throttled to ~10Hz (0.1s sleep)
- Effect animations use appropriate frame rates:
  - Breath: 50ms per frame (20 FPS)
  - Rainbow: 500ms per color (2 colors/sec)
  - CPU: 500ms check interval

### 6.2 Memory Management
- Color objects immutable and hashable → can be pooled
- DeviceStatus reused and updated, not recreated
- UI callbacks use weak references where needed

### 6.3 Threading Best Practices
- Never call UI methods from BLE thread
- All UI updates via `self.after(0, lambda: ...)`
- BLE thread uses asyncio for non-blocking I/O

---

## 7. Testing & Quality Assurance

### 7.1 Unit Test Suite
**Location**: `tests/test_ble_controller.py`

**Test Coverage** (5 tests, all passing):
- ✅ `test_build_packet_and_color_command`: Validates BLE packet format (`[0x7E...0xEF]`)
- ✅ `test_set_speed_clamps_and_updates`: Speed parameter clamping (0–255)
- ✅ `test_is_gatt_timeout_exception_simple`: GATT exception detection (string + type checking)
- ✅ `test_send_packet_handles_exception_and_increases_backoff`: Error handling + exponential backoff
- ✅ `test_read_rssi_prefers_get_rssi_then_backend`: RSSI fallback chain (API → backend → default)

**Run Tests**:
```powershell
# Install dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest -v

# Run specific test
pytest tests/test_ble_controller.py::test_build_packet_and_color_command -v

# Run with coverage
pytest --cov=ble_controller --cov-report=term-missing
```

### 7.2 Syntax Validation
```powershell
# Check for import/syntax errors
python -m py_compile main.py ble_controller.py ui.py models.py services.py components.py app.py

# Check types (optional)
mypy main.py --ignore-missing-imports
```

### 7.3 Manual Testing Checklist
- [ ] UI loads (dark theme, responsive layout)
- [ ] Color picker works (RGB sliders, HEX input)
- [ ] Presets apply correctly
- [ ] Speed slider persists (0–255)
- [ ] Mode buttons switch effects
- [ ] Bluetooth connects (or shows error gracefully)
- [ ] RSSI updates every ~5s (check logs)
- [ ] Config saves to `led_config.json`
- [ ] Logs rotate at 5MB

---

## 8. Deployment & Distribution

### 8.1 Building Standalone EXE

**Prerequisites**:
```powershell
pip install pyinstaller
```

**Build Command**:
```powershell
cd D:\ledcontrol

# Build with console (for debugging)
pyinstaller --onefile --console --name LEDCommander main.py

# Build without console (production)
pyinstaller --onefile --noconsole --name LEDCommander main.py

# With custom icon (if available)
pyinstaller --onefile --noconsole --icon=app.ico --name LEDCommander main.py
```

**Output**:
- **Executable**: `dist/LEDCommander.exe` (~11.5 MB, fully standalone)
- **Build artifacts**: `build/` directory (intermediate files, safe to delete)
- **Spec file**: `LEDCommander.spec` (for future rebuilds)

### 8.2 Post-Build Verification
```powershell
# 1. Verify EXE exists and runs
.\dist\LEDCommander.exe

# 2. Check dependencies bundled
strings dist\LEDCommander.exe | findstr "customtkinter bleak"

# 3. Test config persistence
# - Edit color, switch modes, click Save
# - Close EXE
# - Re-run: verify settings restored from led_config.json

# 4. Check logs
# - led_control.log should be created in working directory
```

### 8.3 Distribution Checklist
- [x] EXE builds successfully (`dist/LEDCommander.exe` created)
- [x] All dependencies bundled (customtkinter, bleak, psutil)
- [x] Tests passing (5/5 in test_ble_controller.py)
- [x] Syntax validated (py_compile check)
- [x] Code modules compile without import errors
- [ ] (Optional) Code signing for Windows SmartScreen
- [ ] (Optional) Installer (Inno Setup / NSIS)
- [ ] Release notes + user guide

### 8.4 Known Limitations
- **Windows only**: Uses WinRT Bluetooth APIs (no macOS/Linux in current build)
- **Requires Bluetooth hardware**: Built-in or USB adapter
- **Device pairing**: Must manually pair LED controller in Windows Settings first
- **Firewall**: May prompt on first run; allow access for best results

---

## 7. Extension Points

### 7.1 Custom Components
```python
# Inherit from ctk.CTkFrame or ctk.CTkLabel
class CustomComponent(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        # Implement _create_widgets()
    
    def update(self, data):
        # Update visual state
        pass
```

### 7.2 New Effect Modes
Follow pattern in `ble_controller.py`:
```python
async def _execute_custom_mode(self):
    while self.current_mode == ColorMode.CUSTOM and self.is_running:
        # Your effect logic
        await self._send_color(color)
        await asyncio.sleep(frame_time)
```

### 7.3 Device-Specific Payload
Override payload format in `_send_color()`:
```python
async def _send_color(self, color: Color):
    if self.client and self.client.is_connected:
        # Customize payload per device
        payload = bytearray([...custom format...])
        await self.client.write_gatt_char(...)
```

---

## 8. Troubleshooting Guide

| Issue | Root Cause | Solution |
|-------|-----------|----------|
| "Device not found" | MAC incorrect or device offline | Check MAC in led_config.json, power device on |
| No BLE communication | UUID mismatch | Verify write_char_uuid with nRF Connect |
| Colors not updating | Event loop stopped | Check logs for exceptions in BLE thread |
| UI frozen | Long-running operation on main thread | Offload to background task |
| Bluetooth not available | Headless/CI environment | Mock BLE in test mode |

---

## 9. Dependencies

```
customtkinter==5.2.2
bleak==2.0.0
psutil==7.1.3
pytest==7.4.0
pytest-asyncio==0.22.0
```

All pure Python, cross-platform (Windows, macOS, Linux for code; Windows-only for BLE).

---

## 10. Version History & Status

| Version | Date | Status | Key Changes | Distribution |
|---------|------|--------|------------|--------------|
| **3.0** | Dec 4, 2025 | ✅ Production Ready | MVVM, modern UI, RSSI, GATT timeout, exponential backoff, speed control, unit tests (5/5), EXE deployment | `dist/LEDCommander.exe` 11.5 MB |
| 2.1 | Nov 2025 | Archived | Config system, logging, Rainbow mode | N/A |
| 1.0 | Oct 2025 | Archived | Basic sliders, initial BLE | N/A |

**Production Checklist**:
- [x] MVVM + Services architecture implemented
- [x] Modern customtkinter UI with dark theme
- [x] BLE communication with protocol layer
- [x] RSSI periodic monitoring (every ~5s)
- [x] GATT timeout detection (hybrid approach: type + heuristic)
- [x] Exponential backoff (2x factor, 300s ceiling)
- [x] Speed control (0–255, persistent)
- [x] Unit test suite (5/5 passing)
- [x] Config persistence (JSON auto-save)
- [x] Standalone EXE deployment (`LEDCommander.exe`)
- [x] Documentation (copilot-instructions.md, AI_AGENT_GUIDE.md)

---

## 11. API Quick Reference

```python
# Color
Color(r, g, b)
Color.from_hex("#RRGGBB")
color.to_hex()
color.apply_brightness(0.5)

# Models
ColorMode.MANUAL | CPU | BREATH | RAINBOW
DeviceStatus(is_connected, device_name, signal_strength, ...)
AppPreferences(brightness, last_color, last_mode, default_speed, ...)

# Services
ConfigService.load_config() / save_config(config)
LoggerService.info/debug/warning/error/success(msg)

# BLE
BleDeviceController(config, on_status, on_color)
controller.start() / stop()
controller.set_color(color)
controller.set_mode(mode)
controller.set_brightness(float)
controller.set_speed(int)  # NEW: 0–255, clamps automatically

# UI
DashboardView()
app.update_device_status(status)
app.controller.emit_color_change(color)

# Application
Application().run()
```

---

## 12. Glossary

- **BLE**: Bluetooth Low Energy (GATT protocol)
- **RSSI**: Received Signal Strength Indicator (dBm, -30 to -120)
- **GATT**: Generic Attribute Profile (BLE service discovery)
- **MVVM**: Model-View-ViewModel architectural pattern
- **Async/Await**: Cooperative multitasking in Python (asyncio)
- **Payload**: Binary data packet sent to device (`[0x7E...0xEF]` format)
- **Event Loop**: Asyncio scheduler for non-blocking coroutines
- **Exponential Backoff**: Retry strategy with increasing delays (2x multiplier, 300s max)
- **Daemon Thread**: Background thread that doesn't block app shutdown

---

**Last Verified**: December 4, 2025  
**EXE Status**: ✅ Built and ready for distribution  
**For questions or updates**: Refer to `README.md` and inline code documentation.
