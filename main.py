import customtkinter as ctk
from components import ColorWheelPicker
from models import ColorPreset, Color
import asyncio
import threading
from bleak import BleakClient, BleakScanner
import psutil
import math
import random
import json
import os
from pathlib import Path
from datetime import datetime

# --- КОНФИГУРАЦИЯ ---
CONFIG_FILE = "led_config.json"
LOG_FILE = "led_control.log"

# Значения по умолчанию
DEFAULT_CONFIG = {
    "target_mac": "FF:FF:10:69:5B:2A",
    "write_char_uuid": "0000fff3-0000-1000-8000-00805f9b34fb",
    "last_color": {"r": 255, "g": 255, "b": 255},
    "brightness": 1.0,
    "theme": "Dark",
    "default_speed": 16
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except:
        pass

def log_message(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {msg}"
    print(log_entry)
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry + "\n")
    except:
        pass

# Загружаем конфиг
CONFIG = load_config()
TARGET_MAC = CONFIG.get("target_mac", "FF:FF:10:69:5B:2A")
WRITE_CHAR_UUID = CONFIG.get("write_char_uuid", "0000fff3-0000-1000-8000-00805f9b34fb")

log_message("=== LED CONTROL STARTED ===")

# --- ЛОГИКА BLUETOOTH (BACKEND) ---
class BleController:
    def __init__(self, status_callback):
        self.client = None
        self.loop = asyncio.new_event_loop()
        self.mode = "MANUAL"
        self.style = "CROSS_FADE"  # Default transition style
        self.running = True
        self.r, self.g, self.b = 0, 0, 0
        # last actually sent color (for smooth transitions)
        self._last_r, self._last_g, self._last_b = 0, 0, 0
        self.status_callback = status_callback 
        self.disconnect_requested = False
        # effect speed (0..255)
        self.speed = CONFIG.get("default_speed", 16)

    def start(self):
        t = threading.Thread(target=self._run_loop, daemon=True)
        t.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._main_task())

    async def _main_task(self):
        while self.running:
            if self.disconnect_requested:
                if self.client and self.client.is_connected:
                    await self.client.disconnect()
                self.disconnect_requested = False
                self.status_callback("DISCONNECTED (MANUAL)", "red")
                log_message("Device disconnected by user")
                await asyncio.sleep(2)
                continue

            self.status_callback("SCANNING...", "orange")
            
            device = None
            if TARGET_MAC:
                try:
                    device = await BleakScanner.find_device_by_address(TARGET_MAC, timeout=5.0)
                    if device:
                        log_message(f"Found device by MAC: {device.name}")
                except Exception as e:
                    log_message(f"MAC scan error: {str(e)[:50]}")
                    pass
            
            if not device:
                # Fallback: поиск по имени
                devices = await BleakScanner.discover(timeout=4.0)
                for d in devices:
                    if d.name and ("ELK" in d.name or "LED" in d.name):
                        device = d
                        log_message(f"Found device by name scan: {device.name}")
                        break
            
            if device:
                self.status_callback(f"CONNECTING: {device.name}", "yellow")
                log_message(f"Connecting to {device.name} ({device.address})")
                try:
                    async with BleakClient(device) as client:
                        self.client = client
                        self.status_callback("CONNECTED: ONLINE", "#00FF00")
                        log_message("BLE Connection established")
                        
                        while client.is_connected and self.running and not self.disconnect_requested:
                            if self.mode == "CPU":
                                cpu = psutil.cpu_percent(interval=0.5)
                                # Градиент: Синий -> Фиолетовый -> Красный
                                if cpu < 40:
                                    self.r, self.g, self.b = 0, 200, 255
                                elif cpu < 70:
                                    self.r, self.g, self.b = 138, 43, 226 # Violet
                                else:
                                    self.r, self.g, self.b = 255, 0, 0
                                await self._send_color(self.r, self.g, self.b)

                            elif self.mode == "BREATH":
                                for i in range(0, 314):
                                    if self.mode != "BREATH" or not client.is_connected: break
                                    val = (math.sin(i/50) + 1) / 2
                                    # Neon Purple Breath
                                    await self._send_color(int(160*val), int(32*val), int(240*val))
                                    await asyncio.sleep(0.02)

                            elif self.mode == "RAINBOW":
                                # Радуга: ROYGBIV цикл
                                colors = [
                                    (255, 0, 0),      # Red
                                    (255, 127, 0),    # Orange
                                    (255, 255, 0),    # Yellow
                                    (0, 255, 0),      # Green
                                    (0, 0, 255),      # Blue
                                    (75, 0, 130),     # Indigo
                                    (148, 0, 211),    # Violet
                                ]
                                idx = 0
                                while self.mode == "RAINBOW" and client.is_connected:
                                    r, g, b = colors[idx % len(colors)]
                                    await self._send_color(r, g, b)
                                    idx += 1
                                    await asyncio.sleep(0.5)

                            elif self.mode == "MANUAL":
                                # Handle transition styles when in MANUAL mode
                                target = (int(self.r), int(self.g), int(self.b))
                                # Map speed (0-255) to timing: higher speed -> faster transitions
                                speed_norm = max(0, min(255, int(self.speed))) / 255.0

                                if self.style == "CROSS_FADE":
                                    # Smoothly interpolate from last sent color to target
                                    last = (self._last_r, self._last_g, self._last_b)
                                    if last != target:
                                        duration = 0.2 + (1.0 - speed_norm) * 4.8  # 0.2 .. 5.0s
                                        steps = max(2, int(duration / 0.05))
                                        for i in range(1, steps + 1):
                                            if self.mode != "MANUAL" or not client.is_connected:
                                                break
                                            t = i / steps
                                            nr = int(last[0] + (target[0] - last[0]) * t)
                                            ng = int(last[1] + (target[1] - last[1]) * t)
                                            nb = int(last[2] + (target[2] - last[2]) * t)
                                            await self._send_color(nr, ng, nb)
                                            await asyncio.sleep(duration / steps)
                                        self._last_r, self._last_g, self._last_b = target
                                    else:
                                        await asyncio.sleep(0.1)

                                elif self.style == "GRADUAL_CHANGE":
                                    # Sweep slowly through a rainbow using small steps
                                    rainbow = [
                                        (255, 0, 0), (255, 127, 0), (255, 255, 0),
                                        (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)
                                    ]
                                    interval = 0.2 + (1.0 - speed_norm) * 2.8  # 0.2 .. 3.0s per step
                                    for col in rainbow:
                                        if self.mode != "MANUAL" or not client.is_connected:
                                            break
                                        await self._send_color(*col)
                                        await asyncio.sleep(interval)

                                elif self.style == "STROBE_FLASH":
                                    # Quick on/off flashing between target and off
                                    flash_interval = max(0.02, 0.3 * (1.0 - speed_norm) + 0.02)  # faster with high speed
                                    await self._send_color(*target)
                                    await asyncio.sleep(0.02)
                                    await self._send_color(0, 0, 0)
                                    await asyncio.sleep(flash_interval)

                                elif self.style == "JUMPING_CHANGE":
                                    # Jump between random presets
                                    presets = ColorPreset.default_presets()
                                    chosen = random.choice(presets)
                                    await self._send_color(*chosen.color.to_tuple())
                                    interval = 0.2 + (1.0 - speed_norm) * 2.8
                                    await asyncio.sleep(interval)

                                else:
                                    # Fallback: direct set
                                    await self._send_color(*target)
                                    await asyncio.sleep(0.1)
                                
                except Exception as e:
                    self.status_callback("CONNECTION LOST", "red")
                    log_message(f"BLE Error: {str(e)[:60]}")
                    await asyncio.sleep(2)
            else:
                self.status_callback("DEVICE NOT FOUND", "red")
                log_message("Device not found during scan")
                await asyncio.sleep(2)

    async def _send_color(self, r, g, b):
        if self.client and self.client.is_connected:
            try:
                payload = bytearray([0x7E, 0x07, 0x05, 0x03, r, g, b, int(self.speed) & 0xFF, 0xEF])
                await self.client.write_gatt_char(WRITE_CHAR_UUID, payload, response=False)
            except Exception as e:
                log_message(f"Send color failed: {e}")

    def set_manual(self, r, g, b):
        self.mode = "MANUAL"
        self.r, self.g, self.b = int(r), int(g), int(b)

    def reconnect(self):
        self.disconnect_requested = True


# --- ИНТЕРФЕЙС (GUI) ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SIGMA LED CONTROL V2.1")
        self.geometry("500x750")
        self.resizable(False, False)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        # Переменные состояния цвета
        self.current_r = 0
        self.current_g = 0
        self.current_b = 0
        self.brightness = CONFIG.get("brightness", 1.0)
        self.hex_entry = None

        self.setup_ui()
        
        self.ble = BleController(self.safe_update_status)
        self.ble.start()
        
        # Восстанавливаем последний цвет
        last_color = CONFIG.get("last_color", {"r": 255, "g": 255, "b": 255})
        self.after(500, lambda: self.restore_last_color(last_color))

    def restore_last_color(self, color):
        try:
            self.slider_r.set(color["r"])
            self.slider_g.set(color["g"])
            self.slider_b.set(color["b"])
            self.on_rgb_change()
        except:
            pass

    def setup_ui(self):
        # Хедер
        self.lbl_title = ctk.CTkLabel(self, text="LED COMMANDER", font=("Impact", 32), text_color="#E0E0E0")
        self.lbl_title.pack(pady=(20, 5))
        
        self.lbl_status = ctk.CTkLabel(self, text="INITIALIZING...", font=("Consolas", 12))
        self.lbl_status.pack(pady=(0, 15))

        # --- ВКЛАДКИ ---
        self.tabs = ctk.CTkTabview(self, width=480, height=600)
        self.tabs.pack(padx=10, pady=10, fill="both", expand=True)

        self.tab_main = self.tabs.add("PALETTE")
        self.tab_modes = self.tabs.add("MODES")
        self.tab_settings = self.tabs.add("SETTINGS")
        self.tab_style = self.tabs.add("STYLE")

        # === ВКЛАДКА 1: ПАЛИТРА И СЛАЙДЕРЫ ===
        
        # Общая Яркость
        ctk.CTkLabel(self.tab_main, text="MASTER BRIGHTNESS", font=("Arial", 11, "bold")).pack(pady=(10, 0))
        self.slider_bright = ctk.CTkSlider(self.tab_main, from_=0, to=1, command=self.update_brightness, progress_color="white")
        self.slider_bright.set(self.brightness)
        self.slider_bright.pack(pady=5, padx=10, fill="x")

        # Сетка пресетов (Кнопки)
        # Presets frame (uses models.ColorPreset)
        self.preset_frame = ctk.CTkFrame(self.tab_main, fg_color="transparent")
        self.preset_frame.pack(pady=10)

        preset_list = ColorPreset.default_presets()
        row = 0
        col = 0
        for p in preset_list:
            hex_col = p.color.to_hex()
            r, g, b = p.color.to_tuple()
            btn = ctk.CTkButton(self.preset_frame, text="", width=40, height=40,
                                fg_color=hex_col, hover_color=hex_col,
                                corner_radius=20,
                                command=lambda r=r, g=g, b=b: self.apply_preset(r, g, b))
            btn.grid(row=row, column=col, padx=8, pady=8)
            col += 1
            if col > 4:
                col = 0
                row += 1

        # Interactive color wheel
        wheel_frame = ctk.CTkFrame(self.tab_main, fg_color="transparent")
        wheel_frame.pack(pady=8)
        try:
            self.color_wheel = ColorWheelPicker(wheel_frame, size=220, on_color_change=self._on_wheel_color_change)
            self.color_wheel.pack()
        except Exception as e:
            log_message(f"Color wheel init failed: {e}")

        # Hex Color Input
        ctk.CTkLabel(self.tab_main, text="HEX COLOR", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        hex_frame = ctk.CTkFrame(self.tab_main, fg_color="transparent")
        hex_frame.pack(pady=5, padx=10, fill="x")
        
        self.hex_entry = ctk.CTkEntry(hex_frame, placeholder_text="#FF5500", width=120)
        self.hex_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(hex_frame, text="APPLY", width=80, command=self.apply_hex_color).pack(side="left", padx=5)

        # Тонкая настройка RGB
        self.rgb_frame = ctk.CTkFrame(self.tab_main)
        self.rgb_frame.pack(pady=10, padx=10, fill="x")

        self.slider_r = self.create_rgb_slider(self.rgb_frame, "R", "#FF4444")
        self.slider_g = self.create_rgb_slider(self.rgb_frame, "G", "#44FF44")
        self.slider_b = self.create_rgb_slider(self.rgb_frame, "B", "#4444FF")

        # === ВКЛАДКА 2: РЕЖИМЫ ===
        ctk.CTkLabel(self.tab_modes, text="SMART EFFECTS", font=("Impact", 20)).pack(pady=20)
        
        btn_cpu = ctk.CTkButton(self.tab_modes, text="RYZEN CPU MONITOR", height=50,
                                fg_color="#222", hover_color="#8A0000", border_width=1, border_color="#555",
                                command=lambda: self.set_mode("CPU"))
        btn_cpu.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.tab_modes, text="Blue = Cold | Red = Hot", text_color="gray", font=("Arial", 9)).pack()

        btn_breath = ctk.CTkButton(self.tab_modes, text="NEON BREATH", height=50,
                                   fg_color="#222", hover_color="#6A0DAD", border_width=1, border_color="#555",
                                   command=lambda: self.set_mode("BREATH"))
        btn_breath.pack(pady=15, padx=20, fill="x")

        btn_rainbow = ctk.CTkButton(self.tab_modes, text="RAINBOW CYCLE", height=50,
                                    fg_color="#222", hover_color="#FF6B6B", border_width=1, border_color="#555",
                                    command=lambda: self.set_mode("RAINBOW"))
        btn_rainbow.pack(pady=15, padx=20, fill="x")
        
        btn_man = ctk.CTkButton(self.tab_modes, text="STOP EFFECTS (MANUAL)", height=40,
                                fg_color="#444",
                                command=lambda: self.set_mode("MANUAL"))
        btn_man.pack(pady=10, padx=20, fill="x")

        # === ВКЛАДКА 3: НАСТРОЙКИ ===
        ctk.CTkLabel(self.tab_settings, text="CONNECTION", font=("Impact", 18)).pack(pady=20)
        
        self.lbl_info = ctk.CTkLabel(self.tab_settings, text=f"Target MAC:\n{TARGET_MAC}", font=("Consolas", 11))
        self.lbl_info.pack(pady=10)

        ctk.CTkButton(self.tab_settings, text="FORCE RECONNECT", fg_color="orange", text_color="black",
                      command=self.force_reconnect).pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(self.tab_settings, text="PREFERENCES", font=("Arial", 12, "bold")).pack(pady=(20, 10))
        # Speed control (0-255)
        ctk.CTkLabel(self.tab_settings, text="EFFECT SPEED", font=("Arial", 10, "bold")).pack(pady=(6, 0))
        self.speed_slider = ctk.CTkSlider(self.tab_settings, from_=0, to=255, command=self.update_speed)
        self.speed_slider.set(CONFIG.get("default_speed", 16))
        self.speed_slider.pack(pady=(4, 8), padx=20, fill="x")

        ctk.CTkButton(self.tab_settings, text="SAVE PREFERENCES", fg_color="#444",
                  command=self.save_preferences).pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(self.tab_settings, text="VIEW LOG FILE", fg_color="#333",
                      command=self.view_log).pack(pady=5, padx=20, fill="x")

        # === ВКЛАДКА 4: СТИЛИ ПЕРЕХОДОВ ===
        ctk.CTkLabel(self.tab_style, text="TRANSITION STYLES", font=("Impact", 18)).pack(pady=20)
        
        # Cross Fade (плавный переход)
        style_frame_1 = ctk.CTkFrame(self.tab_style, fg_color="#2b2b2b", corner_radius=10)
        style_frame_1.pack(pady=10, padx=15, fill="x")
        ctk.CTkLabel(style_frame_1, text="💫 CROSS FADE", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(style_frame_1, text="Smooth blend between colors", text_color="#999", font=("Arial", 10)).pack()
        ctk.CTkSlider(style_frame_1, from_=0.1, to=5.0, command=lambda v: None).pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(style_frame_1, text="Speed (s)", text_color="#666", font=("Arial", 9)).pack()
        ctk.CTkButton(style_frame_1, text="APPLY", fg_color="#4CAF50", command=lambda: self.set_style("CROSS_FADE")).pack(pady=8)
        
        # Gradual Change (медленное плавное изменение)
        style_frame_2 = ctk.CTkFrame(self.tab_style, fg_color="#2b2b2b", corner_radius=10)
        style_frame_2.pack(pady=10, padx=15, fill="x")
        ctk.CTkLabel(style_frame_2, text="🌈 GRADUAL CHANGE", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(style_frame_2, text="Slow color sweep through spectrum", text_color="#999", font=("Arial", 10)).pack()
        ctk.CTkSlider(style_frame_2, from_=0.5, to=10.0, command=lambda v: None).pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(style_frame_2, text="Cycle Time (s)", text_color="#666", font=("Arial", 9)).pack()
        ctk.CTkButton(style_frame_2, text="APPLY", fg_color="#2196F3", command=lambda: self.set_style("GRADUAL_CHANGE")).pack(pady=8)
        
        # Strobe Flash (вспышки)
        style_frame_3 = ctk.CTkFrame(self.tab_style, fg_color="#2b2b2b", corner_radius=10)
        style_frame_3.pack(pady=10, padx=15, fill="x")
        ctk.CTkLabel(style_frame_3, text="⚡ STROBE FLASH", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(style_frame_3, text="Instant on/off flashing effect", text_color="#999", font=("Arial", 10)).pack()
        ctk.CTkSlider(style_frame_3, from_=0.05, to=1.0, command=lambda v: None).pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(style_frame_3, text="Flash Rate (s)", text_color="#666", font=("Arial", 9)).pack()
        ctk.CTkButton(style_frame_3, text="APPLY", fg_color="#FF9800", command=lambda: self.set_style("STROBE_FLASH")).pack(pady=8)
        
        # Jumping Change (скачкообразное изменение)
        style_frame_4 = ctk.CTkFrame(self.tab_style, fg_color="#2b2b2b", corner_radius=10)
        style_frame_4.pack(pady=10, padx=15, fill="x")
        ctk.CTkLabel(style_frame_4, text="🎯 JUMPING CHANGE", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(style_frame_4, text="Step-wise instant color changes", text_color="#999", font=("Arial", 10)).pack()
        ctk.CTkSlider(style_frame_4, from_=0.2, to=3.0, command=lambda v: None).pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(style_frame_4, text="Step Interval (s)", text_color="#666", font=("Arial", 9)).pack()
        ctk.CTkButton(style_frame_4, text="APPLY", fg_color="#E91E63", command=lambda: self.set_style("JUMPING_CHANGE")).pack(pady=8)

    def create_rgb_slider(self, parent, text, color):
        ctk.CTkLabel(parent, text=text, text_color=color, font=("Arial", 12, "bold")).pack()
        slider = ctk.CTkSlider(parent, from_=0, to=255, progress_color=color, button_color=color,
                               command=lambda v: self.on_rgb_change())
        slider.set(0)
        slider.pack(pady=(0, 10))
        return slider

    def apply_preset(self, r, g, b):
        self.slider_r.set(r)
        self.slider_g.set(g)
        self.slider_b.set(b)
        self.on_rgb_change()

    def apply_hex_color(self):
        """Парсит Hex цвет из текстового поля (#RRGGBB или RRGGBB)"""
        hex_str = self.hex_entry.get().strip()
        if hex_str.startswith('#'):
            hex_str = hex_str[1:]
        
        if len(hex_str) == 6:
            try:
                r = int(hex_str[0:2], 16)
                g = int(hex_str[2:4], 16)
                b = int(hex_str[4:6], 16)
                self.slider_r.set(r)
                self.slider_g.set(g)
                self.slider_b.set(b)
                self.on_rgb_change()
                log_message(f"Applied HEX color: #{hex_str.upper()}")
            except:
                self.safe_update_status("Invalid HEX format", "red")
        else:
            self.safe_update_status("HEX must be 6 chars (#RRGGBB)", "red")

    def update_brightness(self, value):
        self.brightness = float(value)
        self.on_rgb_change()

    def update_speed(self, value):
        try:
            s = int(float(value))
        except Exception:
            return
        self.speed = max(0, min(255, s))
        # If BLE controller supports set_speed, call it
        try:
            if hasattr(self.ble, 'set_speed'):
                self.ble.set_speed(self.speed)
            else:
                # For local BleController implementation, set attribute
                setattr(self.ble, 'speed', self.speed)
        except Exception as e:
            log_message(f"Failed to apply speed: {e}")

    def on_rgb_change(self):
        # 1. Берем "сырые" значения со слайдеров
        raw_r = self.slider_r.get()
        raw_g = self.slider_g.get()
        raw_b = self.slider_b.get()

        # 2. Умножаем на яркость
        final_r = int(raw_r * self.brightness)
        final_g = int(raw_g * self.brightness)
        final_b = int(raw_b * self.brightness)
        
        # 3. Отправляем
        self.ble.set_manual(final_r, final_g, final_b)
        
        # 4. Обновляем preview в hex
        hex_color = f"#{final_r:02X}{final_g:02X}{final_b:02X}"
        if self.hex_entry:
            self.hex_entry.delete(0, "end")
            self.hex_entry.insert(0, hex_color)

    def _on_wheel_color_change(self, r: int, g: int, b: int):
        """Handler for color wheel selection - update sliders and apply color."""
        try:
            # set sliders (raw values) then apply
            self.slider_r.set(r)
            self.slider_g.set(g)
            self.slider_b.set(b)
            self.on_rgb_change()
        except Exception as e:
            log_message(f"Wheel color apply failed: {e}")

    def set_mode(self, mode):
        self.ble.mode = mode
        log_message(f"Mode changed to: {mode}")

    def set_style(self, style):
        """Set transition style (CROSS_FADE, GRADUAL_CHANGE, STROBE_FLASH, JUMPING_CHANGE)."""
        self.ble.style = style
        log_message(f"Style changed to: {style}")

    def force_reconnect(self):
        self.ble.reconnect()
        log_message("Force reconnect requested")

    def save_preferences(self):
        """Сохраняет текущие настройки в конфиг"""
        CONFIG["brightness"] = self.brightness
        CONFIG["last_color"] = {
            "r": int(self.slider_r.get()),
            "g": int(self.slider_g.get()),
            "b": int(self.slider_b.get())
        }
        # Save default speed
        try:
            CONFIG["default_speed"] = int(self.speed_slider.get())
        except Exception:
            CONFIG["default_speed"] = CONFIG.get("default_speed", 16)
        save_config(CONFIG)
        self.safe_update_status("Preferences saved!", "green")
        log_message("Preferences saved to config")

    def view_log(self):
        """Открывает лог-файл"""
        if os.path.exists(LOG_FILE):
            try:
                os.startfile(LOG_FILE)
            except:
                self.safe_update_status("Cannot open log file", "red")
        else:
            self.safe_update_status("Log file not found", "orange")

    def safe_update_status(self, text, color):
        self.after(0, lambda: self.lbl_status.configure(text=text, text_color=color))

    def on_closing(self):
        self.ble.running = False
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()