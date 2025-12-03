"""
Bluetooth LE controller with clean separation of concerns.
Manages device connection, communication, and effect modes.
"""

import asyncio
import threading
from typing import Callable, Optional
import psutil
import math

from bleak import BleakClient, BleakScanner
from models import Color, ColorMode, DeviceStatus, DeviceConfig
from services import LoggerService as logger, ConfigService


class BleDeviceController:
    """Manages BLE device connection and communication."""
    
    def __init__(
        self,
        device_config: DeviceConfig,
        on_status_change: Callable[[DeviceStatus], None],
        on_color_received: Callable[[Color], None],
        *,
        auto_reconnect: bool = True,
        reconnect_interval: float = 5.0,
        use_real_device: bool = True,
        initial_speed: int = 0x10
    ):
        self.device_config = device_config
        self.on_status_change = on_status_change
        self.on_color_received = on_color_received
        
        self.client: Optional[BleakClient] = None
        self.loop = asyncio.new_event_loop()
        self.thread: Optional[threading.Thread] = None
        # Reconnect policy
        self.auto_reconnect: bool = bool(auto_reconnect)
        self.reconnect_interval: float = max(1.0, float(reconnect_interval))
        self.use_real_device: bool = bool(use_real_device)

        # Protocol/behavior
        self.speed: int = max(0, min(255, int(initial_speed)))
        # Backoff policy
        self.backoff_factor: float = 2.0
        self.backoff_max: float = 300.0  # max sleep between reconnect attempts
        self.current_backoff: float = float(self.reconnect_interval)
        
        self.is_running = False
        self.current_mode = ColorMode.MANUAL
        self.current_color = Color()
        self.brightness = 1.0
        self.force_disconnect = False
        
        self.status = DeviceStatus()
    
    def start(self):
        """Start BLE controller in background thread."""
        if self.is_running:
            logger.warning("BLE controller already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(
            target=self._run_event_loop,
            daemon=True,
            name="BLE-Controller"
        )
        self.thread.start()
        logger.info("BLE controller started")
    
    def stop(self):
        """Stop BLE controller."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5.0)
        logger.info("BLE controller stopped")
    
    def _run_event_loop(self):
        """Run asyncio event loop."""
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._main_loop())
        except Exception as e:
            logger.error(f"Event loop error: {e}")
        finally:
            self.loop.close()
    
    async def _main_loop(self):
        """Main BLE connection and communication loop."""
        reconnect_count = 0
        max_reconnect_attempts = 10
        
        while self.is_running:
            try:
                # Attempt to find device
                self.status.is_connected = False
                self._emit_status_change("Device search...", "scanning")
                logger.debug("Scanning for BLE device...")
                
                device = await self._find_device()
                
                if not device:
                    reconnect_count += 1
                    if reconnect_count > max_reconnect_attempts:
                        self._emit_status_change("Device not found (max retries)", "error")
                        await asyncio.sleep(30)
                        reconnect_count = 0
                    else:
                        await asyncio.sleep(5)
                    continue
                
                reconnect_count = 0
                # reset backoff on successful discovery
                self.current_backoff = float(self.reconnect_interval)
                
                # Connect to device
                self._emit_status_change(f"Connecting to {device.name}...", "connecting")
                
                async with BleakClient(device) as client:
                    self.client = client
                    self.status.is_connected = True
                    self.status.device_name = device.name or "Unknown Device"
                    self._emit_status_change("Connected", "connected")
                    logger.success(f"Connected to {device.name}")

                    # Communication loop
                    last_rssi_check = 0.0
                    while client.is_connected and self.is_running:
                        if self.force_disconnect:
                            break

                        # Periodic RSSI read (every ~5s)
                        try:
                            now = self.loop.time()
                            if now - last_rssi_check >= 5.0:
                                last_rssi_check = now
                                rssi = await self._read_rssi()
                                if isinstance(rssi, int):
                                    self.status.signal_strength = rssi
                                    self._emit_status_change("RSSI updated", "info")
                        except Exception as e:
                            # Non-critical: RSSI failures should be debug-only
                            logger.debug(f"RSSI read failed: {e}")

                            # Execute current mode
                            await self._execute_mode()
                            await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                logger.debug("BLE task cancelled")
                break
            except Exception as e:
                # Distinguish GATT connection timeouts from other exceptions using exception types when possible
                self.status.is_connected = False
                is_timeout = self._is_gatt_timeout_exception(e)
                msg = str(e)
                if is_timeout:
                    self.status.error_message = "GATT CONN TIMEOUT"
                    self._emit_status_change("GATT CONN TIMEOUT", "error")
                    logger.error(f"GATT CONN TIMEOUT: {msg}")
                else:
                    self.status.error_message = msg[:100]
                    self._emit_status_change(f"Connection error: {msg[:30]}", "error")
                    logger.error(f"BLE error: {e}")

                # Auto-reconnect with exponential backoff
                if self.auto_reconnect:
                    sleep_for = min(self.current_backoff, self.backoff_max)
                    logger.debug(f"Reconnecting in {sleep_for} seconds (backoff)")
                    await asyncio.sleep(sleep_for)
                    # increase backoff
                    self.current_backoff = min(self.backoff_max, max(self.current_backoff * self.backoff_factor, self.reconnect_interval))
                else:
                    await asyncio.sleep(5)
            
            self.client = None
    
    async def _find_device(self):
        """Find BLE device by MAC or name."""
        try:
            # Try to find by MAC
            if self.device_config.target_mac:
                device = await BleakScanner.find_device_by_address(
                    self.device_config.target_mac,
                    timeout=5.0
                )
                if device:
                    return device
            
            # Fallback: scan and search by name
            devices = await BleakScanner.discover(timeout=5.0)
            search_names = ["ELK", "LED", "CTRL", "RGB"]
            
            for device in devices:
                if device.name and any(n in device.name.upper() for n in search_names):
                    return device
            
            return None
        except Exception as e:
            logger.debug(f"Device discovery error: {e}")
            return None
    
    async def _execute_mode(self):
        """Execute current effect mode."""
        if self.current_mode == ColorMode.MANUAL:
            await self._send_color(self.current_color)
        
        elif self.current_mode == ColorMode.CPU:
            await self._execute_cpu_mode()
        
        elif self.current_mode == ColorMode.BREATH:
            await self._execute_breath_mode()
        
        elif self.current_mode == ColorMode.RAINBOW:
            await self._execute_rainbow_mode()
    
    async def _execute_cpu_mode(self):
        """CPU-based color mode."""
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            self.status.cpu_usage = cpu
            
            # Color gradient based on CPU usage
            if cpu < 40:
                color = Color(0, 200, 255)  # Cyan
            elif cpu < 70:
                color = Color(138, 43, 226)  # Violet
            else:
                color = Color(255, 0, 0)  # Red
            
            await self._send_color(color)
        except Exception as e:
            logger.debug(f"CPU mode error: {e}")
    
    async def _execute_breath_mode(self):
        """Neon breath effect."""
        try:
            for i in range(0, 314):
                if self.current_mode != ColorMode.BREATH or not self.is_running:
                    break
                
                val = (math.sin(i / 50) + 1) / 2
                color = Color(
                    r=int(160 * val),
                    g=int(32 * val),
                    b=int(240 * val)
                )
                
                await self._send_color(color)
                await asyncio.sleep(0.02)
        except Exception as e:
            logger.debug(f"Breath mode error: {e}")
    
    async def _execute_rainbow_mode(self):
        """Rainbow cycle effect."""
        try:
            colors = [
                Color(255, 0, 0),      # Red
                Color(255, 127, 0),    # Orange
                Color(255, 255, 0),    # Yellow
                Color(0, 255, 0),      # Green
                Color(0, 0, 255),      # Blue
                Color(75, 0, 130),     # Indigo
                Color(148, 0, 211),    # Violet
            ]
            
            idx = 0
            while self.current_mode == ColorMode.RAINBOW and self.is_running:
                color = colors[idx % len(colors)]
                await self._send_color(color)
                idx += 1
                await asyncio.sleep(0.5)
        except Exception as e:
            logger.debug(f"Rainbow mode error: {e}")
    
    async def _send_color(self, color: Color):
        """Send color to BLE device."""
        # Delegate to new protocol layer
        await self._send_color_command(color)

    def _build_packet(self, cmd: int, p1: int, p2: int, p3: int) -> bytearray:
        """Build device packet using unified protocol.

        Format: [0x7E, 0x07, 0x05, CMD, P1, P2, P3, SPEED, 0xEF]
        """
        return bytearray([
            0x7E,
            0x07,
            0x05,
            cmd & 0xFF,
            p1 & 0xFF,
            p2 & 0xFF,
            p3 & 0xFF,
            int(self.speed) & 0xFF,
            0xEF
        ])

    async def _send_packet(self, payload: bytearray, debug_label: str = "") -> bool:
        """Write packet to device and handle errors centrally.

        Returns True on success, False on failure.
        """
        if not self.client or not self.client.is_connected:
            logger.debug("Attempt to send packet while not connected")
            return False

        try:
            logger.debug(f"Sending packet {debug_label}: {payload.hex()}")
            await self.client.write_gatt_char(self.device_config.write_char_uuid, payload, response=False)
            return True
        except Exception as e:
            msg = str(e)
            # Use improved detection for GATT timeouts
            if self._is_gatt_timeout_exception(e):
                self.status.is_connected = False
                self.status.error_message = "GATT CONN TIMEOUT"
                logger.error(f"GATT CONN TIMEOUT when sending packet: {msg}")
            else:
                # Other write errors are logged as errors as well
                self.status.is_connected = False
                self.status.error_message = msg[:100]
                logger.error(f"BLE write error: {msg}")

            # increase backoff on send failure
            if self.auto_reconnect:
                self.current_backoff = min(self.backoff_max, max(self.current_backoff * self.backoff_factor, self.reconnect_interval))

            return False

    async def _send_color_command(self, color: Color) -> bool:
        """Build and send color command (cmd=0x03)."""
        if not self.client or not self.client.is_connected:
            return False

        try:
            final_color = color.apply_brightness(self.brightness)
            payload = self._build_packet(cmd=0x03, p1=final_color.r, p2=final_color.g, p3=final_color.b)
            ok = await self._send_packet(payload, debug_label="COLOR")
            if ok:
                self.status.current_color = final_color
                try:
                    self.on_color_received(final_color)
                except Exception:
                    logger.debug("on_color_received callback failed")
            return ok
        except Exception as e:
            logger.error(f"_send_color_command error: {e}")
            return False

    async def _send_mode_command(self, mode: ColorMode) -> bool:
        """Build and send mode command (cmd=0x04)."""
        if not self.client or not self.client.is_connected:
            return False

        # Map modes to device codes
        mapping = {
            ColorMode.MANUAL: 0x01,
            ColorMode.CPU: 0x02,
            ColorMode.BREATH: 0x03,
            ColorMode.RAINBOW: 0x04
        }
        cmd_code = mapping.get(mode, 0x01)
        payload = self._build_packet(cmd=0x04, p1=cmd_code, p2=0x00, p3=0x00)
        ok = await self._send_packet(payload, debug_label=f"MODE:{mode.value}")
        if ok:
            self.status.current_mode = mode
        return ok
    
    def set_mode(self, mode: ColorMode):
        """Change effect mode."""
        if self.current_mode != mode:
            self.current_mode = mode
            self.status.current_mode = mode
            logger.info(f"Mode changed: {mode.value}")
            # Try to immediately notify device of mode change (best-effort)
            try:
                if self.loop and self.client and self.client.is_connected:
                    asyncio.run_coroutine_threadsafe(self._send_mode_command(mode), self.loop)
            except Exception:
                logger.debug("Failed to send mode change immediately; will apply in loop")
            self._emit_status_change(f"Mode: {mode.value}", "info")
    
    def set_color(self, color: Color):
        """Set manual color (for MANUAL mode)."""
        self.current_color = color
    
    def set_brightness(self, brightness: float):
        """Set brightness level (0.0 - 1.0)."""
        self.brightness = max(0.0, min(1.0, brightness))

    def set_speed(self, speed: int):
        """Set effect speed (0 - 255). Optionally resend current mode.

        speed is stored and used in subsequent packets.
        """
        s = max(0, min(255, int(speed)))
        if s != self.speed:
            self.speed = s
            logger.info(f"Speed set to {self.speed}")
            # Best-effort: resend current mode so that device adjusts speed
            try:
                if self.loop and self.client and self.client.is_connected:
                    asyncio.run_coroutine_threadsafe(self._send_mode_command(self.current_mode), self.loop)
            except Exception:
                logger.debug("Resend mode on speed change failed")
    
    def request_disconnect(self):
        """Request graceful disconnection."""
        self.force_disconnect = True
        logger.info("Disconnect requested")
    
    def _emit_status_change(self, message: str, status_type: str):
        """Emit status change event."""
        try:
            self.on_status_change(self.status)
        except Exception as e:
            logger.debug(f"Status callback error: {e}")

    def _is_gatt_timeout_exception(self, exc: Exception) -> bool:
        """Heuristic to detect GATT connection timeout across platforms.

        Tries to use Bleak exception types when available, but falls back to
        message/context inspection. Returns True when the exception most likely
        represents a GATT connection timeout (non-recoverable until reconnect).
        """
        try:
            import bleak.exc as bleak_exc
        except Exception:
            bleak_exc = None

        # Check common bleak exception types first
        try:
            if bleak_exc is not None:
                # If it's an instance of BleakError or related, inspect message
                BleakError = getattr(bleak_exc, 'BleakError', None)
                if BleakError and isinstance(exc, BleakError):
                    msg = str(exc).lower()
                    if ('gatt' in msg and 'timeout' in msg) or 'error 8' in msg or 'conn timeout' in msg:
                        return True

            # walk __cause__ and __context__ for nested platform exceptions
            for nested in (getattr(exc, '__cause__', None), getattr(exc, '__context__', None)):
                if nested:
                    nmsg = str(nested).lower()
                    if 'timeout' in nmsg or 'error 8' in nmsg or 'conn timeout' in nmsg:
                        return True

            # final fallback: string matching on the exception itself
            msg = str(exc).lower()
            if ('gatt' in msg and 'timeout' in msg) or 'error 8' in msg or 'conn timeout' in msg:
                return True
        except Exception:
            pass

        return False

    async def _read_rssi(self) -> Optional[int]:
        """Attempt to read RSSI from Bleak client. Returns int dBm or None.

        Tries a public API first if available, otherwise attempts backend-specific access.
        """
        if not self.client or not self.client.is_connected:
            return None

        try:
            # Preferred: Bleak public API (may differ across versions)
            get_rssi = getattr(self.client, "get_rssi", None)
            if callable(get_rssi):
                r = await get_rssi()
                if isinstance(r, int):
                    return r

            # Fallback: backend internals (non-public)
            backend = getattr(self.client, "_backend", None)
            if backend is not None:
                dev = getattr(backend, "_device", None)
                if dev is not None and hasattr(dev, "rssi"):
                    r = getattr(dev, "rssi")
                    try:
                        return int(r)
                    except Exception:
                        return None

        except Exception as e:
            # Non-critical — only debug
            logger.debug(f"RSSI read exception: {e}")
            return None

        return None


class BleApplicationBridge:
    """Bridge connecting UI, BLE controller, and services."""
    
    def __init__(self):
        self.config = ConfigService.get_device_config()
        self.preferences = ConfigService.get_preferences()
        # Pass reconnect preferences and device mode into controller
        self.ble_controller = BleDeviceController(
            self.config,
            self._on_device_status_change,
            self._on_color_received,
            auto_reconnect=self.preferences.auto_reconnect,
            reconnect_interval=self.preferences.reconnect_interval,
            use_real_device=True,
            initial_speed=getattr(self.preferences, 'default_speed', 0x10)
        )
        
        # Both callbacks supported for compatibility
        self.on_ui_update: Optional[Callable] = None
        self.on_status_change: Optional[Callable] = None
    
    @property
    def controller(self):
        """Expose controller for direct access if needed."""
        return self.ble_controller
    
    def initialize(self):
        """Initialize and start the application."""
        self.ble_controller.set_brightness(self.preferences.brightness)
        self.ble_controller.set_color(self.preferences.last_color)
        self.ble_controller.set_mode(self.preferences.last_mode)
        self.ble_controller.start()
        logger.success("Application initialized")
    
    def shutdown(self):
        """Clean shutdown."""
        self.ble_controller.stop()
        logger.info("Application shutdown complete")
    
    def set_color(self, color: Color):
        """Set color from UI."""
        self.ble_controller.set_color(color)
        self.preferences.last_color = color
    
    def set_brightness(self, brightness: float):
        """Set brightness from UI."""
        self.ble_controller.set_brightness(brightness)
        self.preferences.brightness = brightness
    
    def set_mode(self, mode: ColorMode):
        """Set effect mode from UI."""
        self.ble_controller.set_mode(mode)
        self.preferences.last_mode = mode
    
    def save_preferences(self):
        """Save user preferences."""
        ConfigService.save_preferences(self.preferences)
        logger.success("Preferences saved")

    def set_speed(self, speed: int):
        """Proxy to set effect speed on the BLE controller."""
        try:
            self.ble_controller.set_speed(int(speed))
        except Exception as e:
            logger.debug(f"Failed to set speed: {e}")
    
    def _on_device_status_change(self, status: DeviceStatus):
        """Handle device status change."""
        # Support both old and new callback signatures
        if self.on_status_change:
            self.on_status_change(status)
        if self.on_ui_update:
            self.on_ui_update(status)
    
    def _on_color_received(self, color: Color):
        """Handle color confirmation from device."""
        pass  # Update UI if needed
