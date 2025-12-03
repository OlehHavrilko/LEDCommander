"""
Modern UI implementation using component library and clean architecture.
Implements MVVM pattern with responsive dashboard layout.
"""

import customtkinter as ctk
from typing import Optional, Callable
from models import Color, ColorMode, DeviceStatus, AppPreferences, ColorPreset
from services import ConfigService, LoggerService as logger
from components import (
    StatusBadge, ColorPreview, SliderGroup, EffectCard, 
    ToggleButton, StatPanel, DeviceDiscoveryList, ColorScheme
)


class ModernUIController:
    """View controller managing UI state and user interactions."""
    
    def __init__(self):
        self.on_color_changed: Optional[Callable[[Color], None]] = None
        self.on_mode_changed: Optional[Callable[[ColorMode], None]] = None
        self.on_brightness_changed: Optional[Callable[[float], None]] = None
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


class DashboardView(ctk.CTk):
    """Main application window with modern dashboard layout."""
    
    def __init__(self):
        super().__init__()
        self.controller = ModernUIController()
        self.preferences = ConfigService.get_preferences()
        self.device_status = DeviceStatus()
        
        # Configure window
        self.title("LED COMMANDER v3.0 - Professional Control Panel")
        self.geometry("1100x800")
        self.resizable(True, True)
        self.minsize(900, 600)
        
        # Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Build UI
        self._create_layout()
        
        logger.info("Modern UI initialized")
    
    def _create_layout(self):
        """Create main layout structure."""
        # Header with status
        self._create_header()
        
        # Main content area with grid layout
        main_container = ctk.CTkFrame(self, fg_color="#1a1a1a")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel (control)
        left_panel = self._create_left_panel(main_container)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Right panel (info & presets)
        right_panel = self._create_right_panel(main_container)
        right_panel.pack(side="right", fill="both", expand=False, padx=(5, 0))
    
    def _create_header(self):
        """Create application header with status and device info."""
        header = ctk.CTkFrame(self, fg_color="#2b2b2b", height=80)
        header.pack(fill="x", padx=10, pady=(10, 5))
        header.pack_propagate(False)
        
        # Title and logo
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            title_frame,
            text="🎨 LED COMMANDER",
            font=("Arial", 22, "bold"),
            text_color="#ff6b6b"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Professional RGB LED Controller | v3.0",
            font=("Arial", 10),
            text_color="#888"
        ).pack(anchor="w")
        
        # Status indicators
        status_frame = ctk.CTkFrame(header, fg_color="transparent")
        status_frame.pack(side="right", fill="both", padx=15, pady=15)
        
        self.status_badge = StatusBadge(
            status_frame,
            status="disconnected",
            font=("Arial", 12, "bold")
        )
        self.status_badge.pack(side="left", padx=15)
        
        self.signal_label = ctk.CTkLabel(
            status_frame,
            text="Signal: --",
            font=("Courier", 10),
            text_color="#888"
        )
        self.signal_label.pack(side="left", padx=15)
    
    def _create_left_panel(self, parent) -> ctk.CTkFrame:
        """Create left control panel."""
        left_panel = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        
        # Tabs for different sections
        tab_view = ctk.CTkTabview(left_panel)
        tab_view.pack(fill="both", expand=True)
        
        # Tab 1: Color Control
        self._create_color_control_tab(tab_view)
        
        # Tab 2: Effects
        self._create_effects_tab(tab_view)
        
        # Tab 3: Advanced
        self._create_advanced_tab(tab_view)
        
        return left_panel
    
    def _create_color_control_tab(self, tab_view):
        """Create color control tab."""
        color_tab = tab_view.add("🎨 COLOR")
        
        # Color preview
        self.color_preview = ColorPreview(
            color_tab,
            color=(255, 255, 255),
            fg_color="#2b2b2b",
            corner_radius=10
        )
        self.color_preview.pack(fill="x", padx=10, pady=10)
        
        # HEX Input
        hex_frame = ctk.CTkFrame(color_tab, fg_color="transparent")
        hex_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            hex_frame,
            text="HEX Color",
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=(0, 10))
        
        self.hex_entry = ctk.CTkEntry(
            hex_frame,
            placeholder_text="#FFFFFF",
            width=120
        )
        self.hex_entry.pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            hex_frame,
            text="Apply",
            width=80,
            command=self._apply_hex_color
        ).pack(side="left")
        
        # RGB Sliders
        sliders_frame = ctk.CTkFrame(color_tab, fg_color="transparent")
        sliders_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.slider_r = SliderGroup(
            sliders_frame,
            "R",
            "#FF4444",
            lambda v: self._on_rgb_change()
        )
        self.slider_r.pack(fill="x", pady=5)
        
        self.slider_g = SliderGroup(
            sliders_frame,
            "G",
            "#44FF44",
            lambda v: self._on_rgb_change()
        )
        self.slider_g.pack(fill="x", pady=5)
        
        self.slider_b = SliderGroup(
            sliders_frame,
            "B",
            "#4444FF",
            lambda v: self._on_rgb_change()
        )
        self.slider_b.pack(fill="x", pady=5)
        
        # Brightness control
        brightness_frame = ctk.CTkFrame(color_tab, fg_color="transparent")
        brightness_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            brightness_frame,
            text="BRIGHTNESS",
            font=("Arial", 11, "bold"),
            text_color="#FFD700"
        ).pack()
        
        self.brightness_slider = ctk.CTkSlider(
            brightness_frame,
            from_=0,
            to=1,
            progress_color="#FFD700",
            button_color="#FFD700",
            command=self._on_brightness_change
        )
        self.brightness_slider.set(self.preferences.brightness)
        self.brightness_slider.pack(fill="x", padx=5, pady=5)
        
        self.brightness_label = ctk.CTkLabel(
            brightness_frame,
            text=f"{int(self.preferences.brightness * 100)}%",
            font=("Courier", 10)
        )
        self.brightness_label.pack()
    
    def _create_effects_tab(self, tab_view):
        """Create effects/modes tab."""
        effects_tab = tab_view.add("✨ EFFECTS")
        
        # Effects grid
        effects_frame = ctk.CTkFrame(effects_tab, fg_color="transparent")
        effects_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Manual mode
        self.card_manual = EffectCard(
            effects_frame,
            "MANUAL",
            "Direct color control\nNo animations",
            "🖌️",
            on_click=lambda: self._set_mode(ColorMode.MANUAL),
            selected=True
        )
        self.card_manual.pack(fill="x", pady=5)
        
        # CPU Monitor mode
        self.card_cpu = EffectCard(
            effects_frame,
            "CPU MONITOR",
            "Color follows CPU load\nBlue (cold) → Red (hot)",
            "📊",
            on_click=lambda: self._set_mode(ColorMode.CPU)
        )
        self.card_cpu.pack(fill="x", pady=5)
        
        # Breath effect
        self.card_breath = EffectCard(
            effects_frame,
            "NEON BREATH",
            "Smooth pulsing animation\nPurple glow effect",
            "💜",
            on_click=lambda: self._set_mode(ColorMode.BREATH)
        )
        self.card_breath.pack(fill="x", pady=5)
        
        # Rainbow effect
        self.card_rainbow = EffectCard(
            effects_frame,
            "RAINBOW CYCLE",
            "Full spectrum rotation\nSmooth color transitions",
            "🌈",
            on_click=lambda: self._set_mode(ColorMode.RAINBOW)
        )
        self.card_rainbow.pack(fill="x", pady=5)
    
    def _create_advanced_tab(self, tab_view):
        """Create advanced settings tab."""
        advanced_tab = tab_view.add("⚙️ ADVANCED")
        
        # Auto-reconnect toggle
        reconnect_frame = ctk.CTkFrame(advanced_tab, fg_color="transparent")
        reconnect_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            reconnect_frame,
            text="Auto-Reconnect",
            font=("Arial", 10, "bold")
        ).pack(anchor="w")
        
        self.toggle_reconnect = ToggleButton(
            reconnect_frame,
            text_on="ENABLED",
            text_off="DISABLED",
            width=150
        )
        self.toggle_reconnect.pack(pady=5)
        
        # Device info
        info_frame = ctk.CTkFrame(advanced_tab, fg_color="#2b2b2b", corner_radius=10)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        self.device_info_panel = StatPanel(
            info_frame,
            "Device Information"
        )
        self.device_info_panel.pack(fill="both", expand=True)
        
        # Buttons
        button_frame = ctk.CTkFrame(advanced_tab, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="🔄 Force Reconnect",
            fg_color="#8a0000",
            command=self._force_reconnect
        ).pack(fill="x", pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="💾 Save Preferences",
            fg_color="#2e7d32",
            command=self._save_preferences
        ).pack(fill="x", pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="📋 View Log",
            fg_color="#1976d2",
            command=self._view_log
        ).pack(fill="x", pady=5)
    
    def _create_right_panel(self, parent) -> ctk.CTkFrame:
        """Create right info panel."""
        right_panel = ctk.CTkFrame(parent, fg_color="#2b2b2b", width=300, corner_radius=10)
        right_panel.pack_propagate(False)
        
        # Presets section
        presets_label = ctk.CTkLabel(
            right_panel,
            text="QUICK PRESETS",
            font=("Arial", 12, "bold")
        )
        presets_label.pack(fill="x", padx=15, pady=(15, 10))
        
        # Preset buttons
        presets_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        presets_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for preset in ColorPreset.default_presets():
            btn = ctk.CTkButton(
                presets_frame,
                text="",
                fg_color=preset.color.to_hex(),
                hover_color=preset.color.to_hex(),
                width=40,
                height=40,
                corner_radius=20,
                command=lambda p=preset: self._apply_preset(p)
            )
            btn.pack(padx=5, pady=5, side="left", fill="both", expand=True)
        
        # Stats section
        stats_label = ctk.CTkLabel(
            right_panel,
            text="STATUS",
            font=("Arial", 12, "bold")
        )
        stats_label.pack(fill="x", padx=15, pady=(15, 10))
        
        self.stats_panel = StatPanel(
            right_panel,
            "Connection Stats",
            fg_color="#1a1a1a",
            corner_radius=8
        )
        self.stats_panel.pack(fill="both", expand=True, padx=10, pady=10)
        
        return right_panel
    
    def _on_rgb_change(self):
        """Handle RGB slider change."""
        color = Color(
            r=self.slider_r.get(),
            g=self.slider_g.get(),
            b=self.slider_b.get()
        )
        self.color_preview.set_color(color.to_tuple())
        self.hex_entry.delete(0, "end")
        self.hex_entry.insert(0, color.to_hex())
        self.controller.emit_color_change(color)
        logger.debug(f"Color changed: {color.to_hex()}")
    
    def _on_brightness_change(self, value: float):
        """Handle brightness change."""
        brightness = float(value)
        self.brightness_label.configure(text=f"{int(brightness * 100)}%")
        self.controller.emit_brightness_change(brightness)
        logger.debug(f"Brightness changed: {brightness * 100}%")
    
    def _apply_hex_color(self):
        """Apply hex color input."""
        try:
            hex_str = self.hex_entry.get().strip()
            color = Color.from_hex(hex_str)
            self.slider_r.set(color.r)
            self.slider_g.set(color.g)
            self.slider_b.set(color.b)
            self._on_rgb_change()
        except ValueError as e:
            logger.error(f"Invalid HEX color: {e}")
    
    def _apply_preset(self, preset: ColorPreset):
        """Apply color preset."""
        self.slider_r.set(preset.color.r)
        self.slider_g.set(preset.color.g)
        self.slider_b.set(preset.color.b)
        self._on_rgb_change()
        logger.info(f"Preset applied: {preset.name}")
    
    def _set_mode(self, mode: ColorMode):
        """Set active effect mode."""
        # Update card selections
        for card, m in [
            (self.card_manual, ColorMode.MANUAL),
            (self.card_cpu, ColorMode.CPU),
            (self.card_breath, ColorMode.BREATH),
            (self.card_rainbow, ColorMode.RAINBOW)
        ]:
            card.set_selected(m == mode)
        
        self.controller.emit_mode_change(mode)
        logger.info(f"Mode changed: {mode.value}")
    
    def _force_reconnect(self):
        """Force device reconnection."""
        logger.warning("Force reconnect requested")
    
    def _save_preferences(self):
        """Save current preferences."""
        ConfigService.save_preferences(self.preferences)
        logger.success("Preferences saved")
    
    def _view_log(self):
        """Open log file."""
        import os
        try:
            os.startfile("led_control.log")
        except:
            logger.error("Cannot open log file")
    
    def update_device_status(self, status: DeviceStatus):
        """Update UI with device status."""
        self.device_status = status
        
        # Update status badge
        if status.is_connected:
            self.status_badge.set_status("connected")
        else:
            self.status_badge.set_status("disconnected")
        
        # Update signal
        signal_bars = self._rssi_to_bars(status.signal_strength)
        self.signal_label.configure(text=f"Signal: {signal_bars}")
        
        # Update stats
        self.stats_panel.set_stat("Status", "✓ Connected" if status.is_connected else "✗ Offline")
        self.stats_panel.set_stat("Mode", status.current_mode.value)
        self.stats_panel.set_stat("Signal", f"{status.signal_strength} dBm")
        if status.cpu_usage is not None:
            self.stats_panel.set_stat("CPU Usage", f"{status.cpu_usage:.1f}%")
    
    @staticmethod
    def _rssi_to_bars(rssi: int) -> str:
        """Convert RSSI to signal strength bars."""
        if rssi >= -50:
            return "████ Excellent"
        elif rssi >= -60:
            return "███░ Good"
        elif rssi >= -70:
            return "██░░ Fair"
        elif rssi >= -80:
            return "█░░░ Weak"
        else:
            return "░░░░ Very Weak"
    
    def on_closing(self):
        """Handle window closing."""
        logger.info("Application closing")
        self.destroy()


def run_modern_ui():
    """Launch modern UI application."""
    logger.separator("LED COMMANDER v3.0")
    app = DashboardView()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    run_modern_ui()
