# Testing Guide - LED COMMANDER v3.0 ELK-BLEDOM UI

## Quick Start

### 1. Launch Application
```powershell
cd D:\ledcontrol
.\venv\Scripts\Activate.ps1
python app.py
```

### 2. Expected UI

**Header** (top bar):
- Shows: "LED COMMANDER v3.0" on left (red)
- Center: Device status info
- Right: Settings button (⚙️)

**Left Navigation**:
- 4 buttons: 🎨 Adjust, ✨ Style, ⏰ Schedule, 🔗 Connect
- 🎨 Adjust is selected by default (red background)

**Content Area** (Adjust tab by default):
- Color wheel preview circle (top-left)
- RGB values display (R, G, B)
- HEX color input box
- Color wheel picker (if available)
- Brightness slider (0-100%)
- Grid of color preset buttons
- Color preview box

## UI Section Tests

### Test 1: Navigation
**Steps:**
1. Click "✨ Style" button in left nav
2. Verify Style tab content appears
3. Click "⏰ Schedule" 
4. Verify Schedule tab with two cards
5. Click "🔗 Connect"
6. Verify device list appears
7. Click "🎨 Adjust" again
8. Verify Adjust tab returns

**Expected Result**: Navigation buttons highlight correctly, content changes

---

### Test 2: Color Control (Adjust Tab)
**Steps:**
1. Ensure on Adjust tab
2. Type "#FF0000" in HEX input
3. Click "Apply" button
4. Verify color preview box turns red
5. Verify RGB display shows: R: 255, G: 0, B: 0
6. Verify HEX label shows: #FF0000

**Expected Result**: HEX parsing works, color updates correctly

---

### Test 3: Color Presets
**Steps:**
1. Click a preset color button (e.g., green)
2. Verify color preview updates
3. Verify HEX input updates
4. Verify RGB display updates

**Expected Result**: Preset colors apply instantly

---

### Test 4: Brightness Control
**Steps:**
1. Move brightness slider to 50%
2. Verify label shows "50%"
3. Move to 100%
4. Verify label shows "100%"
5. Move to 0%
6. Verify label shows "0%"

**Expected Result**: Slider responds smoothly, percentage updates

---

### Test 5: Effect Selection (Style Tab)
**Steps:**
1. Click "✨ Style" button
2. Click on "Rainbow Cycle" effect
3. Verify effect row highlights (white text, darker background)
4. Verify "► SELECTED" indicator appears
5. Click another effect (e.g., "Neon Breath")
6. Verify previous effect deselects, new one highlights

**Expected Result**: Effects highlight on selection, only one active at a time

---

### Test 6: Speed and Brightness in Style
**Steps:**
1. On Style tab, move Speed slider
2. Verify speed number updates in real-time
3. Move Brightness slider
4. Verify percentage updates

**Expected Result**: Both sliders respond smoothly

---

### Test 7: Schedule Tab
**Steps:**
1. Click "⏰ Schedule" button
2. Verify two cards: "Schedule On" and "Schedule Off"
3. In "Schedule On" card:
   - Click time input, type "14:30"
   - Click day buttons (MO, WE, FR)
   - Verify selected days turn red
4. In "Schedule Off" card:
   - Click time input, type "22:00"
   - Click day buttons (SU)

**Expected Result**: Schedule cards functional, days toggle color

---

### Test 8: Connect Device Tab
**Steps:**
1. Click "🔗 Connect" button
2. Verify device list shows:
   - Device name (e.g., "ELK-BLEDOM")
   - MAC address
   - Connection status (✓ Connected or ○ Disconnected)
   - "Connect"/"Disconnect" button
   - "Delete" button
3. Verify "Scan for Devices" button exists

**Expected Result**: Device list displays correctly, buttons functional

---

### Test 9: Settings Modal
**Steps:**
1. Click "⚙️ Settings" button in header
2. Modal window opens
3. Verify settings fields:
   - Auto-Reconnect checkbox
   - Reconnect Interval field (e.g., "5.0")
   - Theme radio buttons (Dark/Light)
4. Modify a setting
5. Click "Save" button
6. Modal closes
7. Verify changes persisted in config file

**Expected Result**: Modal opens, saves preferences correctly

---

### Test 10: Color Wheel (if available)
**Steps:**
1. On Adjust tab
2. Click anywhere on the color wheel
3. Verify RGB values update
4. Verify color preview updates
5. Verify HEX value updates

**Expected Result**: Color wheel selects colors correctly

---

## Integration Tests

### Test 11: BLE Bridge Connection
**Prerequisites**: Device configured in `led_config.json`

**Steps:**
1. Launch app with BLE device nearby
2. Check logs for:
   - "Connecting to [Device Name]..."
   - "Connected" message
   - RSSI value (e.g., "-65 dBm")
3. Verify header shows:
   - Device name
   - ✓ Connect status
   - RSSI value

**Expected Result**: Device connects, status updates in header

---

### Test 12: Color Change to Device
**Prerequisites**: BLE device connected

**Steps:**
1. Adjust tab
2. Change color (wheel, preset, or HEX)
3. Check device: LED should change color
4. Verify status callback received (check logs)

**Expected Result**: Color commands sent to device

---

### Test 13: Effect Change to Device
**Prerequisites**: BLE device connected

**Steps:**
1. Style tab
2. Select different effects
3. Device should display corresponding effect
4. Adjust speed slider
5. Device effect speed should change

**Expected Result**: Mode/speed commands sent to device

---

## Performance Tests

### Test 14: UI Responsiveness
**Steps:**
1. Rapidly click color buttons
2. Drag sliders quickly
3. Switch between tabs rapidly
4. Monitor for freezing or lag

**Expected Result**: UI remains responsive, no noticeable delays

---

### Test 15: Memory Stability
**Steps:**
1. Run app for 5+ minutes
2. Repeatedly switch tabs
3. Continuously adjust sliders
4. Monitor task manager for memory growth

**Expected Result**: Memory usage stable, no leaks

---

## Debug Commands

### Check Configuration
```python
from services import ConfigService
config = ConfigService.load_config()
print(config)
```

### Check Preferences
```python
from services import ConfigService
prefs = ConfigService.get_preferences()
print(f"Brightness: {prefs.brightness}")
print(f"Last Color: {prefs.last_color.to_hex()}")
print(f"Last Mode: {prefs.last_mode.value}")
```

### Check Device Status
```python
from models import DeviceStatus
# Access from bridge.controller.status
print(f"Connected: {status.is_connected}")
print(f"RSSI: {status.signal_strength}")
print(f"Mode: {status.current_mode.value}")
```

### Enable Debug Logging
```python
import os
os.environ['LOG_LEVEL'] = 'DEBUG'
# Then run: python app.py
```

### Test Color Parsing
```python
from models import Color
c = Color.from_hex("#FF00FF")
print(c.to_hex())  # Should print: #FF00FF
```

---

## Common Issues & Fixes

### Issue: UI doesn't appear
**Fix**: Check if window is behind other windows. Try Alt+Tab.

### Issue: Color wheel missing
**Fix**: This is a known limitation. HEX input and presets will still work.

### Issue: Settings don't save
**Fix**: Check file permissions on `led_config.json`. Run as admin if needed.

### Issue: Device doesn't connect
**Fix**: 
1. Verify MAC address in `led_config.json`
2. Check device is powered and discoverable
3. Check Windows Bluetooth settings
4. Check firewall settings

### Issue: Sliders stutter
**Fix**: Check CPU usage, close other applications

---

## Automated Test Script

```bash
#!/bin/bash
# Run basic validation tests

echo "Testing imports..."
python -c "from ui import DashboardView; print('✓ UI imports')"
python -c "from components import NavButton; print('✓ Components import')"
python -c "from models import Color; print('✓ Models import')"

echo ""
echo "Testing color parsing..."
python -c "from models import Color; c = Color.from_hex('#FF00FF'); assert c.r == 255; print('✓ HEX parsing')"
python -c "from models import Color; c = Color(100, 150, 200); assert c.to_hex() == '#6496C8'; print('✓ HEX conversion')"

echo ""
echo "Testing effect list..."
python -c "from ui import EFFECTS_LIST; assert len(EFFECTS_LIST) > 0; print(f'✓ {len(EFFECTS_LIST)} effects loaded')"

echo ""
echo "All tests passed! ✓"
```

---

## Checklist Before Release

- [ ] All imports successful
- [ ] Navigation buttons work
- [ ] All tabs accessible
- [ ] Color controls functional
- [ ] Effect selection working
- [ ] Schedule cards interactive
- [ ] Device list displays
- [ ] Settings modal works
- [ ] Header shows device status
- [ ] Colors persist after restart
- [ ] No console errors
- [ ] UI scales properly on resize
- [ ] Keyboard navigation works (Tab key)
- [ ] BLE events flow correctly
- [ ] Device commands send (with hardware)

---

**Version**: 3.0 (ELK-BLEDOM Redesign)  
**Last Updated**: December 4, 2025
