# LED COMMANDER v3.0 - ELK-BLEDOM UI Redesign

## 🎨 Overview

The GUI has been completely redesigned to match the layout and user experience of the ELK-BLEDOM mobile app, adapted for desktop. The new design uses a vertical navigation sidebar, intuitive section-based layout, and dark theme inspired by modern mobile applications.

## 📐 New Layout Architecture

### **Header (Top Bar)**
- **Left**: Application title "LED COMMANDER v3.0" in red (#ff6b6b)
- **Center**: Device status summary showing:
  - Device name
  - MAC address
  - Connection status (✓ or ✗)
  - RSSI signal strength in dBm
- **Right**: Settings button (⚙️) that opens a modal window

### **Left Navigation Panel**
- Vertical sidebar (width: ~140px) with dark background (#171717)
- Four main navigation buttons with icons:
  - 🎨 **Adjust** - Color control
  - ✨ **Style** - Effects and modes
  - ⏰ **Schedule** - Turn on/off scheduling
  - 🔗 **Connect** - Device connection management
- Active button is highlighted with red background (#ff6b6b) and white text
- Icons and text labels for clarity

### **Content Area (Right)**
- Responsive main content area with scrollable sections
- Each section displays when its navigation button is clicked
- Dark background (#0a0a0a) with accent colors

## 📑 Sections

### **1. Adjust (🎨 Color Control)**
- **Color Wheel**: Interactive HSV color picker (300x300px)
- **Color Preview**: Small circle showing current color
- **RGB Display**: Live R, G, B values in separate lines with matching colors
- **HEX Input**: Text field for entering hex codes (e.g., #FF5500) with Apply button
- **Brightness Slider**: 0-100% with label and percentage display
- **Color Presets**: Grid of 12 pre-defined color buttons (red, green, blue, cyan, magenta, yellow, etc.)

**Events Flow:**
```
Color Wheel Change
    ↓
_on_color_wheel_change(r, g, b)
    ↓
controller.emit_color_change(Color(r, g, b))
    ↓
BleApplicationBridge.set_color()
    ↓
BleDeviceController.set_color()
```

### **2. Style (✨ Effects)**
List of 12 effects/modes with selection highlighting:
- Seven Color Cross Fade → RAINBOW
- Red/Green/Blue/Yellow/Cyan/Purple/White Gradual Change → MANUAL
- Red Green Cross Fade → MANUAL
- CPU Monitor (Breath) → CPU
- Neon Breath → BREATH
- Rainbow Cycle → RAINBOW

Features:
- **Effect Selection**: Click to highlight and select effect (white text, darker background, "► SELECTED" indicator)
- **Speed Slider**: 0-255 value with numeric display
- **Brightness Slider**: Same as Adjust tab (0-100%)

**Events Flow:**
```
Effect Selected
    ↓
_on_effect_selected(effect_id)
    ↓
controller.emit_mode_change(ColorMode)
    ↓
BleApplicationBridge.set_mode()
```

### **3. Schedule (⏰ Scheduling)**
Two scheduling cards: "Schedule On" and "Schedule Off"

Each card contains:
- **Toggle**: Enable/disable scheduling
- **Time Input**: HH:MM format
- **Day Selection**: 7 buttons (MO, TU, WE, TH, FR, SA, SU)
  - Unselected: dark background (#3a3a3a)
  - Selected: red background (#ff6b6b)

**Future Enhancement**: Store schedule data in `AppPreferences` and send to device via BLE protocol.

### **4. Connect (🔗 Device Connection)**
- **Device List**: Shows configured device(s)
  - Device name
  - MAC address
  - Connection status (✓ Connected / ○ Disconnected)
  - **Connect/Disconnect** button
  - **Delete** button (removes device from config)
- **Scan Button**: Placeholder for future BLE device discovery

## 🔧 New Components (components.py)

### **NavButton**
- Navigation button with icon and text
- Highlights when selected (red background, black text)
- Click handler for section switching

### **EffectListItem**
- List item for effects with selection state
- Shows effect name and selection indicator (► SELECTED)
- Color-coded borders and backgrounds based on state

### **ScheduleCard**
- Card container for schedule settings
- Time input field
- Day toggle buttons
- Callbacks for time and day changes

### **DeviceListItem**
- Device information display
- Connection status indicator
- Connect/Disconnect and Delete buttons
- Updates connection state dynamically

## 🔌 Integration with Architecture

### **ModernUIController Events**
All UI interactions emit events through the controller:
- `on_color_changed(Color)` - Color selection from wheel or presets
- `on_mode_changed(ColorMode)` - Effect mode selection
- `on_brightness_changed(float)` - Brightness slider (0.0-1.0)
- `on_speed_changed(int)` - Speed slider (0-255)

### **BleApplicationBridge Methods**
The bridge now supports all controller events:
- `set_color(Color)` - Update device color
- `set_mode(ColorMode)` - Change effect mode
- `set_brightness(float)` - Adjust brightness
- `set_speed(int)` - Set effect speed
- `on_status_change` - Callback for device status updates

### **Status Updates**
- Device status is updated every 1 second via `_schedule_status_update()`
- Header and device list reflect current connection state
- RSSI signal strength displayed in real-time

## 🎯 Color Scheme

### **Dark Theme (Default)**
- **Background**: #0a0a0a (very dark)
- **Sidebar**: #171717 (dark grey)
- **Cards**: #2b2b2b (medium grey)
- **Accents**: #ff6b6b (red), #e0e0e0 (light grey)
- **Text**: #e0e0e0 (default), #ffffff (highlighted)
- **RGB Display**: #ff6b6b (R), #6bffb6 (G), #6b9eff (B)

## 📁 Modified Files

### **ui.py** (Complete Rewrite)
- `ModernUIController` - Manages UI events with new `on_speed_changed` callback
- `DashboardView` - Main window with new layout
- `_create_layout()` - Header + left nav + content sections
- `_build_adjust_section()` - Color wheel, preview, RGB, brightness, presets, HEX input
- `_build_style_section()` - Effects list, speed slider, brightness
- `_build_schedule_section()` - Schedule On/Off cards
- `_build_connect_section()` - Device list
- `_open_settings_modal()` - Settings window with auto-reconnect, interval, theme
- `update_device_status()` - Updates header and device list
- `run_modern_ui()` - Entry point

### **components.py** (Extended)
- `NavButton` - NEW: Navigation button component
- `EffectListItem` - NEW: Effect list item with selection
- `ScheduleCard` - NEW: Schedule configuration card
- `DeviceListItem` - NEW: Device display with connection controls
- (Existing components preserved: ColorWheelPicker, ColorPreview, etc.)

### **app.py** (Updated)
- Enhanced initialization logging
- New event handler: `_handle_speed_change()`
- Periodic status updates: `_schedule_status_update()`
- Improved shutdown logging

### **ble_controller.py** (Enhanced)
- `BleApplicationBridge` now exposes:
  - `controller` property for direct access
  - `on_status_change` callback (in addition to `on_ui_update`)
  - Supports both callback signatures for compatibility

## 🚀 Usage

### Running the Application
```powershell
.\venv\Scripts\Activate.ps1
python app.py
```

### Sections Navigation
1. Click navigation buttons on the left to switch sections
2. Each section maintains its own state
3. Settings button (⚙️) opens a modal for preferences

### Color Control (Adjust Tab)
1. Use the color wheel to select hue and saturation
2. Click presets for quick color changes
3. Or enter a HEX code and click Apply
4. Adjust brightness with the slider

### Effect Selection (Style Tab)
1. Click an effect name to select it
2. Adjust speed and brightness as needed
3. Effect immediately applies to device

### Scheduling (Schedule Tab)
1. Configure "Schedule On" time and days
2. Configure "Schedule Off" time and days
3. (Future: send to device)

### Device Management (Connect Tab)
1. View configured device with MAC address
2. Check connection status
3. (Future: scan and add new devices)

## 🔄 Data Flow Example: Color Change

```
User clicks color wheel
    ↓
_on_color_wheel_change(r, g, b)
    ↓
DashboardView.current_color = Color(r, g, b)
    ↓
DashboardView._update_color_display()
    ↓
ModernUIController.emit_color_change(Color)
    ↓
Application._handle_color_change(Color)
    ↓
BleApplicationBridge.set_color(Color)
    ↓
BleApplicationBridge.preferences.last_color = Color
    ↓
BleDeviceController.set_color(Color)
    ↓
BleDeviceController._send_color(Color) [in async loop]
    ↓
Device receives color packet and updates LED
    ↓
BleDeviceController.on_status_change() emitted
    ↓
BleApplicationBridge._on_device_status_change()
    ↓
Application._schedule_status_update() callback
    ↓
DashboardView.update_device_status(status)
    ↓
Header and device list updated
```

## 📝 Notes

### Architecture Preservation
- ✅ No breaking changes to models, services, or ble_controller architecture
- ✅ All business logic remains in appropriate layers
- ✅ UI only handles presentation and event emission
- ✅ Full MVVM + Services pattern maintained

### Future Enhancements
- [ ] BLE device scanning in Connect tab
- [ ] Actual schedule persistence and execution
- [ ] Music/Mic mode visualizers
- [ ] Light theme support
- [ ] Preset customization UI
- [ ] Macro/Sequence editor
- [ ] Statistics and history panels

### Testing Checklist
- ✅ All imports successful
- ✅ Color wheel integration working
- ✅ HEX input parsing working
- ✅ Navigation buttons highlight correctly
- ✅ Sections switch on button click
- ✅ Settings modal opens/closes
- ✅ Device status updates display
- [ ] Live BLE device testing (requires hardware)

## 🎓 Developer Notes

### Adding a New Effect
1. Add to `EFFECTS_LIST` in ui.py
2. Map to `ColorMode` in the list tuple
3. If new mode, add to `models.ColorMode` enum
4. Implement in `BleDeviceController._execute_mode()`

### Customizing Colors
Edit `ColorScheme.DARK` in components.py:
```python
"accent": "#ff6b6b",        # Main accent color
"card_bg": "#2b2b2b",       # Card backgrounds
"border": "#444444",        # Border color
```

### Working with Modals
Use `ctk.CTkToplevel()` for child windows (example in `_open_settings_modal()`):
```python
settings_window = ctk.CTkToplevel(self)
settings_window.title("Settings")
settings_window.geometry("400x300")
```

### Emitting UI Events
In any section, call controller methods to emit events:
```python
self.controller.emit_color_change(Color(255, 0, 0))
self.controller.emit_mode_change(ColorMode.RAINBOW)
self.controller.emit_brightness_change(0.75)
self.controller.emit_speed_change(200)
```

---

**Last Updated**: December 4, 2025  
**Version**: 3.0 (ELK-BLEDOM Redesign)  
**Architecture**: MVVM + Services Pattern
