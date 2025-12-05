"""
LED COMMANDER v3.0 - ELK-BLEDOM inspired desktop UI.
Modern dashboard with vertical navigation and effect controls.
"""

import customtkinter as ctk
from typing import Optional, Callable, Dict, List
from core.models import Color, ColorMode, DeviceStatus, AppPreferences, ColorPreset
from core.services import ConfigService, LoggerService as logger
from ui.components import (
    NavButton, EffectListItem, ScheduleCard, DeviceListItem,
    ColorPreview, ColorWheelPicker, SliderGroup
)


class ModernUIController:
    """View controller managing UI state and user interactions."""
    
    def __init__(self):
        self.on_color_changed: Optional[Callable[[Color], None]] = None
        self.on_mode_changed: Optional[Callable[[ColorMode], None]] = None
        self.on_brightness_changed: Optional[Callable[[float], None]] = None
        self.on_speed_changed: Optional[Callable[[int], None]] = None
        self.on_preferences_saved: Optional[Callable[[], None]] = None
    
    def emit_color_change(self, color: Color):
        """Emit color change event."""
        if self.on_color_changed:
            self.on_color_changed(color)
    
    def emit_mode_change(self, mode: ColorMode):
        """Emit mode change event."""
        if self.on_mode_changed:
            self.on_mode_changed(mode)
    
    def emit_brightness_change(self, brightness: float):
        """Emit brightness change event."""
        if self.on_brightness_changed:
            self.on_brightness_changed(brightness)
    
    def emit_speed_change(self, speed: int):
        """Emit speed change event."""
        if self.on_speed_changed:
            self.on_speed_changed(speed)


# ======================== EFFECTS MAPPING ========================

# Map effect names to ColorModes and IDs
EFFECTS_LIST = [
    ("Seven Color Cross Fade", ColorMode.RAINBOW),
    ("Red Gradual Change", ColorMode.MANUAL),
    ("Green Gradual Change", ColorMode.MANUAL),
    ("Blue Gradual Change", ColorMode.MANUAL),
    ("Yellow Gradual Change", ColorMode.MANUAL),
    ("Cyan Gradual Change", ColorMode.MANUAL),
    ("Purple Gradual Change", ColorMode.MANUAL),
    ("White Gradual Change", ColorMode.MANUAL),
    ("Red Green Cross Fade", ColorMode.MANUAL),
    ("CPU Monitor (Breath)", ColorMode.CPU),
    ("Neon Breath", ColorMode.BREATH),
    ("Rainbow Cycle", ColorMode.RAINBOW),
]


class DashboardView(ctk.CTk):
    """Main application window with ELK-BLEDOM inspired layout."""
    
    def __init__(self):
        super().__init__()
        self.controller = ModernUIController()
        self.preferences = ConfigService.get_preferences()
        self.device_status = DeviceStatus()
        
        # State tracking
        self.current_section = "Adjust"
        self.current_effect_index = 0
        self.current_color = Color(255, 255, 255)
        self.current_brightness = 1.0
        self.current_speed = 128
        
        # Configure window
        self.title("LED COMMANDER v3.0")
        self.geometry("1200x800")
        self.resizable(True, True)
        self.minsize(1000, 700)
        
        # Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Build UI
        self._create_layout()
        
        logger.info("ELK-BLEDOM UI initialized")
    
    def _create_layout(self):
        """Create main layout structure."""
        # Header
        self._create_header()
        
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="#0a0a0a")
        main_container.pack(fill="both", expand=True)
        
        # Left navigation
        left_nav = ctk.CTkFrame(main_container, fg_color="#171717", width=140)
        left_nav.pack(side="left", fill="y")
        left_nav.pack_propagate(False)
        self._create_left_nav(left_nav)
        
        # Content area (main frame)
        self.content_area = ctk.CTkFrame(main_container, fg_color="#0a0a0a")
        self.content_area.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        
        # Create sections
        self._create_sections()
    
    def _create_header(self):
        """Create top header with device status."""
        header = ctk.CTkFrame(self, fg_color="#2b2b2b", height=70)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Left: title
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        ctk.CTkLabel(
            left,
            text="LED COMMANDER v3.0",
            font=("Arial", 16, "bold"),
            text_color="#ff6b6b"
        ).pack(anchor="w")
        
        # Center: device status
        self.device_summary = ctk.CTkLabel(
            left,
            text="Device: -- | MAC: -- | Connect: ✗ | RSSI: -- dBm",
            font=("Arial", 9),
            text_color="#bbb"
        )
        self.device_summary.pack(anchor="w", pady=(2, 0))
        
        # Right: settings button
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right", padx=15, pady=10)
        
        self.settings_btn = ctk.CTkButton(
            right,
            text="⚙️ Settings",
            width=100,
            height=36,
            command=self._open_settings_modal
        )
        self.settings_btn.pack()
    
    def _create_left_nav(self, parent):
        """Create left navigation panel."""
        nav_title = ctk.CTkLabel(
            parent,
            text="MENU",
            font=("Arial", 10, "bold"),
            text_color="#ff6b6b"
        )
        nav_title.pack(pady=(15, 10), padx=10)
        
        # Navigation buttons
        self.nav_buttons: Dict[str, NavButton] = {}
        
        for section_name, icon in [
            ("Adjust", "🎨"),
            ("Style", "✨"),
            ("Schedule", "⏰"),
            ("Connect", "🔗"),
        ]:
            btn = NavButton(
                parent,
                text=section_name,
                icon=icon,
                on_click=self._on_nav_click,
                fg_color="#2b2b2b",
                text_color="#e0e0e0",
                hover_color="#3a3a3a"
            )
            btn.pack(fill="x", padx=8, pady=6)
            self.nav_buttons[section_name] = btn
        
        # Set Adjust as default selected
        self.nav_buttons["Adjust"].set_selected(True)
        
        # Spacer
        spacer = ctk.CTkFrame(parent, fg_color="transparent", height=20)
        spacer.pack(fill="y", expand=True)
    
    def _on_nav_click(self, section_name: str):
        """Handle navigation button click."""
        # Update selection
        for name, btn in self.nav_buttons.items():
            btn.set_selected(name == section_name)
        
        self.current_section = section_name
        self._show_section(section_name)
    
    def _create_sections(self):
        """Create all content sections."""
        # Create frames for each section (stacked)
        self.sections: Dict[str, ctk.CTkFrame] = {}
        
        for section_name in ["Adjust", "Style", "Schedule", "Connect"]:
            frame = ctk.CTkFrame(self.content_area, fg_color="#0a0a0a")
            frame.pack(fill="both", expand=True, padx=0, pady=0)
            self.sections[section_name] = frame
        
        # Build each section
        self._build_adjust_section(self.sections["Adjust"])
        self._build_style_section(self.sections["Style"])
        self._build_schedule_section(self.sections["Schedule"])
        self._build_connect_section(self.sections["Connect"])
        
        # Show Adjust by default
        self._show_section("Adjust")
    
    def _show_section(self, section_name: str):
        """Show/hide sections."""
        for name, frame in self.sections.items():
            if name == section_name:
                frame.pack(fill="both", expand=True, padx=0, pady=0)
            else:
                frame.pack_forget()
    
    # ======================== ADJUST SECTION ========================
    
    def _build_adjust_section(self, parent):
        """Build color adjustment section."""
        # Scroll container for responsiveness
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="#0a0a0a")
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        ctk.CTkLabel(
            scroll_frame,
            text="Color Adjustment",
            font=("Arial", 14, "bold"),
            text_color="#e0e0e0"
        ).pack(anchor="w", pady=(0, 15))
        
        # Main container: color wheel + controls
        main_box = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        main_box.pack(fill="both", expand=True)
        
        # Left: color wheel
        left_col = ctk.CTkFrame(main_box, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Color preview
        self.color_preview = ctk.CTkFrame(
            left_col,
            fg_color=self.current_color.to_hex(),
            width=120,
            height=120,
            border_width=2,
            border_color="#444444",
            corner_radius=8
        )
        self.color_preview.pack(pady=(0, 10))
        self.color_preview.pack_propagate(False)
        
        # RGB values display
        rgb_frame = ctk.CTkFrame(left_col, fg_color="transparent")
        rgb_frame.pack(fill="x", pady=(0, 15))
        
        self.rgb_r_label = ctk.CTkLabel(
            rgb_frame,
            text=f"R: {self.current_color.r}",
            font=("Arial", 10),
            text_color="#ff6b6b"
        )
        self.rgb_r_label.pack(anchor="w", pady=2)
        
        self.rgb_g_label = ctk.CTkLabel(
            rgb_frame,
            text=f"G: {self.current_color.g}",
            font=("Arial", 10),
            text_color="#6bffb6"
        )
        self.rgb_g_label.pack(anchor="w", pady=2)
        
        self.rgb_b_label = ctk.CTkLabel(
            rgb_frame,
            text=f"B: {self.current_color.b}",
            font=("Arial", 10),
            text_color="#6b9eff"
        )
        self.rgb_b_label.pack(anchor="w", pady=2)
        
        self.hex_label = ctk.CTkLabel(
            rgb_frame,
            text=self.current_color.to_hex(),
            font=("Arial", 11, "bold"),
            text_color="#e0e0e0"
        )
        self.hex_label.pack(anchor="w", pady=(5, 0))
        
        # Color wheel
        try:
            self.color_wheel = ColorWheelPicker(
                left_col,
                size=250,
                on_color_change=self._on_color_wheel_change
            )
            self.color_wheel.pack(pady=10)
        except Exception as e:
            logger.warning(f"Color wheel failed: {e}")
        
        # Right: controls
        right_col = ctk.CTkFrame(main_box, fg_color="transparent", width=200)
        right_col.pack(side="right", fill="both", expand=False, padx=(15, 0))
        right_col.pack_propagate(False)
        
        # Brightness
        ctk.CTkLabel(
            right_col,
            text="Brightness",
            font=("Arial", 12, "bold"),
            text_color="#e0e0e0"
        ).pack(anchor="w", pady=(0, 8))
        
        self.brightness_slider = ctk.CTkSlider(
            right_col,
            from_=0,
            to=1.0,
            number_of_steps=100,
            command=self._on_brightness_change,
            progress_color="#ff6b6b"
        )
        self.brightness_slider.set(self.current_brightness)
        self.brightness_slider.pack(fill="x", pady=(0, 5))
        
        self.brightness_label = ctk.CTkLabel(
            right_col,
            text=f"{int(self.current_brightness * 100)}%",
            font=("Arial", 10),
            text_color="#bbb"
        )
        self.brightness_label.pack(anchor="e", pady=(0, 15))
        
        # Presets
        ctk.CTkLabel(
            right_col,
            text="Presets",
            font=("Arial", 12, "bold"),
            text_color="#e0e0e0"
        ).pack(anchor="w", pady=(0, 8))
        
        presets_frame = ctk.CTkFrame(right_col, fg_color="transparent")
        presets_frame.pack(fill="x", pady=(0, 15))
        
        for preset in ColorPreset.default_presets()[:12]:  # Show first 12 presets
            btn = ctk.CTkButton(
                presets_frame,
                text="",
                width=30,
                height=30,
                fg_color=preset.color.to_hex(),
                hover_color=preset.color.to_hex(),
                border_color="#444444",
                border_width=1,
                command=lambda p=preset: self._apply_preset(p)
            )
            btn.pack(side="left", padx=3, pady=3)
        
        # HEX input
        ctk.CTkLabel(
            right_col,
            text="HEX Input",
            font=("Arial", 12, "bold"),
            text_color="#e0e0e0"
        ).pack(anchor="w", pady=(15, 8))
        
        hex_frame = ctk.CTkFrame(right_col, fg_color="transparent")
        hex_frame.pack(fill="x", pady=(0, 15))
        
        self.hex_entry = ctk.CTkEntry(
            hex_frame,
            placeholder_text="#FFFFFF",
            font=("Arial", 11),
            width=120
        )
        self.hex_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.hex_entry.insert(0, self.current_color.to_hex())
        
        hex_btn = ctk.CTkButton(
            hex_frame,
            text="Apply",
            width=60,
            command=self._apply_hex_color
        )
        hex_btn.pack(side="left")
    
    def _on_color_wheel_change(self, r: int, g: int, b: int):
        """Handle color wheel change."""
        self.current_color = Color(r, g, b)
        self._update_color_display()
        self.controller.emit_color_change(self.current_color)
    
    def _on_brightness_change(self, value: float):
        """Handle brightness slider change."""
        self.current_brightness = float(value)
        self.brightness_label.configure(text=f"{int(self.current_brightness * 100)}%")
        self.controller.emit_brightness_change(self.current_brightness)
    
    def _apply_preset(self, preset: ColorPreset):
        """Apply color preset."""
        self.current_color = preset.color
        self.hex_entry.delete(0, "end")
        self.hex_entry.insert(0, self.current_color.to_hex())
        self._update_color_display()
        self.controller.emit_color_change(self.current_color)
    
    def _apply_hex_color(self):
        """Apply HEX color input."""
        try:
            hex_value = self.hex_entry.get()
            self.current_color = Color.from_hex(hex_value)
            self._update_color_display()
            self.controller.emit_color_change(self.current_color)
        except Exception as e:
            logger.warning(f"Invalid HEX: {e}")
    
    def _update_color_display(self):
        """Update color preview and RGB display."""
        hex_color = self.current_color.to_hex()
        self.color_preview.configure(fg_color=hex_color)
        
        # Update RGB labels
        if hasattr(self, 'rgb_r_label'):
            self.rgb_r_label.configure(text=f"R: {self.current_color.r}")
        if hasattr(self, 'rgb_g_label'):
            self.rgb_g_label.configure(text=f"G: {self.current_color.g}")
        if hasattr(self, 'rgb_b_label'):
            self.rgb_b_label.configure(text=f"B: {self.current_color.b}")
        if hasattr(self, 'hex_label'):
            self.hex_label.configure(text=hex_color)
    
    # ======================== STYLE SECTION ========================
    
    def _build_style_section(self, parent):
        """Build effects/style section."""
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="#0a0a0a")
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        ctk.CTkLabel(
            scroll_frame,
            text="Effects & Styles",
            font=("Arial", 14, "bold"),
            text_color="#e0e0e0"
        ).pack(anchor="w", pady=(0, 15))
        
        # Effects list
        effects_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        effects_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        self.effect_items: List[EffectListItem] = []
        for idx, (effect_name, color_mode) in enumerate(EFFECTS_LIST):
            item = EffectListItem(
                effects_frame,
                effect_name=effect_name,
                effect_id=idx,
                on_select=self._on_effect_selected,
                selected=(idx == 0),
                fg_color="#2b2b2b" if idx == 0 else "#1a1a1a"
            )
            item.pack(fill="x", pady=4)
            self.effect_items.append(item)
        
        # Divider
        ctk.CTkFrame(scroll_frame, fg_color="#444444", height=1).pack(fill="x", pady=15)
        
        # Speed control
        ctk.CTkLabel(
            scroll_frame,
            text="Speed",
            font=("Arial", 12, "bold"),
            text_color="#e0e0e0"
        ).pack(anchor="w", pady=(0, 8))
        
        speed_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        speed_frame.pack(fill="x", pady=(0, 15))
        
        self.speed_slider = ctk.CTkSlider(
            speed_frame,
            from_=0,
            to=255,
            number_of_steps=255,
            command=self._on_speed_change,
            progress_color="#ff6b6b"
        )
        self.speed_slider.set(self.current_speed)
        self.speed_slider.pack(fill="x", side="left", expand=True)
        
        self.speed_label = ctk.CTkLabel(
            speed_frame,
            text=f"{int(self.current_speed)}",
            font=("Arial", 10),
            text_color="#bbb",
            width=40
        )
        self.speed_label.pack(side="left", padx=(10, 0))
        
        # Brightness control (same as Adjust)
        ctk.CTkLabel(
            scroll_frame,
            text="Brightness",
            font=("Arial", 12, "bold"),
            text_color="#e0e0e0"
        ).pack(anchor="w", pady=(15, 8))
        
        brightness_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        brightness_frame.pack(fill="x")
        
        self.style_brightness_slider = ctk.CTkSlider(
            brightness_frame,
            from_=0,
            to=1.0,
            number_of_steps=100,
            command=self._on_brightness_change,
            progress_color="#ff6b6b"
        )
        self.style_brightness_slider.set(self.current_brightness)
        self.style_brightness_slider.pack(fill="x", side="left", expand=True)
        
        self.style_brightness_label = ctk.CTkLabel(
            brightness_frame,
            text=f"{int(self.current_brightness * 100)}%",
            font=("Arial", 10),
            text_color="#bbb",
            width=40
        )
        self.style_brightness_label.pack(side="left", padx=(10, 0))
    
    def _on_effect_selected(self, effect_id: int):
        """Handle effect selection."""
        self.current_effect_index = effect_id
        effect_name, color_mode = EFFECTS_LIST[effect_id]
        
        # Update UI highlighting
        for idx, item in enumerate(self.effect_items):
            item.set_selected(idx == effect_id)
        
        # Emit mode change
        self.controller.emit_mode_change(color_mode)
        logger.info(f"Effect selected: {effect_name}")
    
    def _on_speed_change(self, value: float):
        """Handle speed slider change."""
        self.current_speed = int(value)
        self.speed_label.configure(text=str(self.current_speed))
        self.controller.emit_speed_change(self.current_speed)
    
    # ======================== SCHEDULE SECTION ========================
    
    def _build_schedule_section(self, parent):
        """Build scheduling section."""
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="#0a0a0a")
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        ctk.CTkLabel(
            scroll_frame,
            text="Schedule",
            font=("Arial", 14, "bold"),
            text_color="#e0e0e0"
        ).pack(anchor="w", pady=(0, 15))
        
        # Schedule On
        self.schedule_on_card = ScheduleCard(
            scroll_frame,
            title="Schedule On",
            on_time_change=lambda t: self._on_schedule_change("on", "time", t),
            on_day_toggle=lambda d, v: self._on_schedule_change("on", "day", d, v)
        )
        self.schedule_on_card.pack(fill="x", pady=(0, 15))
        
        # Schedule Off
        self.schedule_off_card = ScheduleCard(
            scroll_frame,
            title="Schedule Off",
            on_time_change=lambda t: self._on_schedule_change("off", "time", t),
            on_day_toggle=lambda d, v: self._on_schedule_change("off", "day", d, v)
        )
        self.schedule_off_card.pack(fill="x")
    
    def _on_schedule_change(self, schedule_type: str, change_type: str, *args):
        """Handle schedule changes."""
        logger.info(f"Schedule {schedule_type} {change_type} changed: {args}")
        # Store in preferences (implementation depends on requirements)
    
    # ======================== CONNECT DEVICE SECTION ========================
    
    def _build_connect_section(self, parent):
        """Build device connection section."""
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="#0a0a0a")
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        ctk.CTkLabel(
            scroll_frame,
            text="Connect Device",
            font=("Arial", 14, "bold"),
            text_color="#e0e0e0"
        ).pack(anchor="w", pady=(0, 15))
        
        # Device list
        self.device_items: List[DeviceListItem] = []
        
        # Add configured device
        config = ConfigService.get_device_config()
        device_item = DeviceListItem(
            scroll_frame,
            device_name=config.device_name,
            device_mac=config.target_mac,
            is_connected=self.device_status.is_connected,
            on_connect=self._on_device_connect,
            on_delete=self._on_device_delete
        )
        device_item.pack(fill="x", pady=10)
        self.device_items.append(device_item)
        
        # Scan button (placeholder)
        ctk.CTkButton(
            scroll_frame,
            text="Scan for Devices",
            command=self._on_scan_devices,
            fg_color="#3a3a3a",
            height=40
        ).pack(fill="x", pady=15)
    
    def _on_device_connect(self):
        """Handle device connect."""
        logger.info("Device connect requested")
    
    def _on_device_delete(self):
        """Handle device delete."""
        logger.info("Device delete requested")
    
    def _on_scan_devices(self):
        """Handle scan devices."""
        logger.info("Scanning for devices...")
    
    # ======================== SETTINGS MODAL ========================
    
    def _open_settings_modal(self):
        """Open settings modal window."""
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        
        # Center on parent
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 300) // 2
        settings_window.geometry(f"+{x}+{y}")
        
        # Content
        frame = ctk.CTkScrollableFrame(settings_window, fg_color="#1a1a1a")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Auto-reconnect
        ctk.CTkLabel(frame, text="Auto-Reconnect", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 5))
        auto_reconnect = ctk.CTkCheckBox(
            frame,
            text="Enable automatic reconnection",
            onvalue=True,
            offvalue=False
        )
        auto_reconnect.pack(anchor="w")
        auto_reconnect.select() if self.preferences.auto_reconnect else auto_reconnect.deselect()
        
        # Reconnect interval
        ctk.CTkLabel(frame, text="Reconnect Interval (seconds)", font=("Arial", 11, "bold")).pack(anchor="w", pady=(15, 5))
        interval_entry = ctk.CTkEntry(frame, placeholder_text="5.0")
        interval_entry.pack(fill="x", pady=(0, 10))
        interval_entry.insert(0, str(self.preferences.reconnect_interval))
        
        # Theme
        ctk.CTkLabel(frame, text="Theme", font=("Arial", 11, "bold")).pack(anchor="w", pady=(15, 5))
        theme_var = ctk.StringVar(value=self.preferences.theme)
        ctk.CTkRadioButton(frame, text="Dark", variable=theme_var, value="dark").pack(anchor="w")
        ctk.CTkRadioButton(frame, text="Light", variable=theme_var, value="light").pack(anchor="w")
        
        # Save button
        def save_settings():
            self.preferences.auto_reconnect = auto_reconnect.get()
            try:
                self.preferences.reconnect_interval = float(interval_entry.get())
            except ValueError:
                pass
            self.preferences.theme = theme_var.get()
            ConfigService.save_preferences(self.preferences)
            settings_window.destroy()
            logger.success("Settings saved")
        
        ctk.CTkButton(
            frame,
            text="Save",
            command=save_settings,
            height=40
        ).pack(fill="x", pady=(20, 0))
    
    # ======================== PUBLIC METHODS ========================
    
    def update_device_status(self, status: DeviceStatus):
        """Update device status display."""
        self.device_status = status
        
        # Update header
        connect_status = "✓" if status.is_connected else "✗"
        rssi_text = f"{status.signal_strength} dBm" if status.signal_strength else "--"
        # Get MAC from config
        from core.services import ConfigService
        config = ConfigService.get_device_config()
        mac = config.target_mac if config.target_mac else "--"
        summary = f"Device: {status.device_name} | MAC: {mac} | Connect: {connect_status} | RSSI: {rssi_text}"
        
        self.device_summary.configure(text=summary)
        
        # Update device list if visible
        if self.device_items:
            self.device_items[0].update_connection_status(status.is_connected)
    
    def on_closing(self):
        """Handle window closing."""
        logger.info("Closing LED COMMANDER v3.0")
        self.destroy()


def run_modern_ui():
    """Launch modern UI application."""
    logger.separator("LED COMMANDER v3.0 - ELK-BLEDOM UI")
    app = DashboardView()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    run_modern_ui()
