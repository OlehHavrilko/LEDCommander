import customtkinter as ctk
import asyncio
import threading
from bleak import BleakClient, BleakScanner
import psutil
import math

# --- НАСТРОЙКИ ---
# Ваш MAC адрес из nRF Connect. 
# Если поставить None, будет искать по имени, но по MAC надежнее и быстрее.
TARGET_MAC = "FF:FF:10:69:5B:2A"
WRITE_CHAR_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"

# ЦВЕТОВАЯ СХЕМА (Sigma/Dark)
COLOR_BG = "#1a1a1a"
COLOR_ACCENT = "#8a0000" # Темно-красный
COLOR_TEXT = "#e0e0e0"

class BleController:
    def __init__(self, status_callback):
        self.client = None
        self.loop = asyncio.new_event_loop()
        self.mode = "MANUAL" 
        self.running = True
        self.r, self.g, self.b = 0, 0, 0
        self.status_callback = status_callback # Функция для обновления текста в окне

    def start(self):
        t = threading.Thread(target=self._run_loop, daemon=True)
        t.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._main_task())

    async def _main_task(self):
        while self.running:
            self.status_callback("Поиск устройства...", "orange")
            device = await BleakScanner.find_device_by_address(TARGET_MAC, timeout=5.0)
            
            if not device:
                # Если не нашли по MAC, пробуем сканировать всё (резервный вариант)
                devices = await BleakScanner.discover(timeout=3.0)
                for d in devices:
                    if d.name and ("ELK" in d.name or "LED" in d.name):
                        device = d
                        break
            
            if device:
                self.status_callback(f"Подключение к {device.name}...", "yellow")
                try:
                    async with BleakClient(device) as client:
                        self.client = client
                        self.status_callback("CONNECTED: ACTIVE", "#00ff00")
                        
                        while client.is_connected and self.running:
                            if self.mode == "CPU":
                                # Логика для Ryzen 5 5600
                                cpu = psutil.cpu_percent(interval=0.2)
                                # Градиент от Синего (холодно) к Красному (горячо)
                                if cpu < 40: # Простой
                                    self.r, self.g, self.b = 0, 255, 255 # Cyan
                                elif cpu < 70: # Нагрузка
                                    self.r, self.g, self.b = 255, 165, 0 # Orange
                                else: # Перегрузка
                                    self.r, self.g, self.b = 255, 0, 0 # Red
                                
                                await self._send_color(self.r, self.g, self.b)

                            elif self.mode == "BREATH":
                                # Эффект дыхания
                                for i in range(0, 628): # 2*PI * 100
                                    if self.mode != "BREATH": break
                                    val = (math.sin(i/100) + 1) / 2
                                    # Фиолетовый неон
                                    await self._send_color(int(138*val), int(43*val), int(226*val))
                                    await asyncio.sleep(0.02)
                                
                            elif self.mode == "MANUAL":
                                await self._send_color(self.r, self.g, self.b)
                                await asyncio.sleep(0.1)
                                
                except Exception as e:
                    self.status_callback(f"Ошибка: {str(e)[:20]}", "red")
                    await asyncio.sleep(2) # Пауза перед переподключением
            else:
                self.status_callback("Устройство не найдено", "red")
                await asyncio.sleep(2)

    async def _send_color(self, r, g, b):
        if self.client and self.client.is_connected:
            try:
                payload = bytearray([0x7E, 0x07, 0x05, 0x03, r, g, b, 0x10, 0xEF])
                await self.client.write_gatt_char(WRITE_CHAR_UUID, payload, response=False)
            except:
                pass

    def set_manual(self, r, g, b):
        self.mode = "MANUAL"
        self.r, self.g, self.b = int(r), int(g), int(b)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SIGMA LED CONTROL")
        self.geometry("400x600")
        self.resizable(False, False)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.ble = BleController(self.update_status)
        self.ble.start()
        
        self.setup_ui()

    def setup_ui(self):
        # Заголовок
        self.head = ctk.CTkLabel(self, text="CONTROLLER V1", font=("Impact", 28), text_color=COLOR_TEXT)
        self.head.pack(pady=(30, 5))
        
        # Статус
        self.lbl_status = ctk.CTkLabel(self, text="INITIALIZING...", font=("Consolas", 12))
        self.lbl_status.pack(pady=5)

        # Рамка управления
        self.frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Слайдеры
        self.create_slider("RED", "#ff4444", self.frame, lambda v: self.update_manual())
        self.slider_r = self.last_slider
        
        self.create_slider("GREEN", "#44ff44", self.frame, lambda v: self.update_manual())
        self.slider_g = self.last_slider
        
        self.create_slider("BLUE", "#4444ff", self.frame, lambda v: self.update_manual())
        self.slider_b = self.last_slider

        # Кнопки режимов
        ctk.CTkLabel(self.frame, text="MODES", font=("Impact", 18)).pack(pady=(20, 10))
        
        self.btn_cpu = ctk.CTkButton(self.frame, text="RYZEN CPU MONITOR", 
                                     fg_color="#333", hover_color=COLOR_ACCENT, 
                                     command=lambda: self.set_mode("CPU"))
        self.btn_cpu.pack(pady=5, padx=20, fill="x")

        self.btn_breath = ctk.CTkButton(self.frame, text="NEON BREATH", 
                                        fg_color="#333", hover_color="#6a0dad",
                                        command=lambda: self.set_mode("BREATH"))
        self.btn_breath.pack(pady=5, padx=20, fill="x")

    def create_slider(self, text, color, parent, cmd):
        ctk.CTkLabel(parent, text=text, text_color=color, font=("Arial", 12, "bold")).pack(pady=(10,0))
        slider = ctk.CTkSlider(parent, from_=0, to=255, command=cmd, progress_color=color, button_color=color)
        slider.set(0)
        slider.pack(pady=5)
        self.last_slider = slider

    def update_manual(self):
        self.ble.set_manual(self.slider_r.get(), self.slider_g.get(), self.slider_b.get())

    def set_mode(self, mode):
        self.ble.mode = mode

    def update_status(self, text, color):
        # Обновление GUI должно быть в главном потоке
        self.lbl_status.configure(text=text, text_color=color)

    def on_closing(self):
        self.ble.running = False
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()