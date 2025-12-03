"""
Reusable UI component library for consistent, modern interface.
Implements design system with custom widgets built on customtkinter.
"""

import customtkinter as ctk
from typing import Callable, Optional, Tuple, List
from enum import Enum


class ColorScheme(Enum):
    """Color scheme definitions for light/dark themes."""
    DARK = {
        "bg": "#1a1a1a",
        "fg": "#e0e0e0",
        "accent": "#8a0000",
        "accent_light": "#ff6b6b",
        "success": "#00ff00",
        "warning": "#ffa500",
        "error": "#ff0000",
        "card_bg": "#2b2b2b",
        "border": "#444444"
    }
    LIGHT = {
        "bg": "#f5f5f5",
        "fg": "#1a1a1a",
        "accent": "#d32f2f",
        "accent_light": "#ff6b6b",
        "success": "#2e7d32",
        "warning": "#f57c00",
        "error": "#c62828",
        "card_bg": "#ffffff",
        "border": "#cccccc"
    }


class StatusBadge(ctk.CTkLabel):
    """Status indicator badge with color-coded status."""
    
    def __init__(self, parent, status: str = "disconnected", **kwargs):
        super().__init__(parent, **kwargs)
        self.status = status
        self._update_appearance()
    
    def set_status(self, status: str):
        """Update badge status: connected, connecting, disconnected, error."""
        self.status = status
        self._update_appearance()
    
    def _update_appearance(self):
        """Update visual appearance based on status."""
        status_config = {
            "connected": ("● ONLINE", "#00ff00"),
            "connecting": ("⟳ CONNECTING", "#ffa500"),
            "disconnected": ("○ OFFLINE", "#ff0000"),
            "error": ("⚠ ERROR", "#ff0000"),
        }
        text, color = status_config.get(self.status, ("?", "#808080"))
        self.configure(text=text, text_color=color)


class ColorPreview(ctk.CTkFrame):
    """Visual color preview with RGB values and hex display."""
    
    def __init__(self, parent, color: Tuple[int, int, int] = (255, 255, 255), **kwargs):
        super().__init__(parent, **kwargs)
        self.color = color
        self._create_widgets()
    
    def _create_widgets(self):
        """Create color preview layout."""
        # Color box
        self.color_box = ctk.CTkFrame(
            self, 
            fg_color=f"#{self.color[0]:02x}{self.color[1]:02x}{self.color[2]:02x}",
            width=100, 
            height=100,
            border_width=2,
            border_color="#666"
        )
        self.color_box.pack(side="left", padx=10, pady=10)
        
        # Info frame
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", padx=10, fill="both", expand=True)
        
        hex_value = f"#{self.color[0]:02X}{self.color[1]:02X}{self.color[2]:02X}"
        ctk.CTkLabel(
            info_frame, 
            text=hex_value, 
            font=("Courier", 16, "bold")
        ).pack()
        
        rgb_text = f"RGB({self.color[0]}, {self.color[1]}, {self.color[2]})"
        ctk.CTkLabel(
            info_frame, 
            text=rgb_text, 
            font=("Courier", 12),
            text_color="#888"
        ).pack()
    
    def set_color(self, color: Tuple[int, int, int]):
        """Update displayed color."""
        self.color = color
        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        self.color_box.configure(fg_color=hex_color)


class SliderGroup(ctk.CTkFrame):
    """Grouped RGB sliders with labels and value display."""
    
    def __init__(self, parent, label: str, color: str, on_change: Callable, **kwargs):
        super().__init__(parent, **kwargs)
        self.label = label
        self.color = color
        self.on_change = on_change
        self.slider = None
        self.value_label = None
        self._create_widgets()
    
    def _create_widgets(self):
        """Create slider layout."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=(10, 0))
        
        ctk.CTkLabel(
            header,
            text=self.label,
            text_color=self.color,
            font=("Arial", 11, "bold"),
            width=40
        ).pack(side="left")
        
        self.value_label = ctk.CTkLabel(
            header,
            text="0",
            font=("Courier", 10),
            width=40
        )
        self.value_label.pack(side="right")
        
        self.slider = ctk.CTkSlider(
            self,
            from_=0,
            to=255,
            progress_color=self.color,
            button_color=self.color,
            command=self._on_slider_change
        )
        self.slider.set(0)
        self.slider.pack(fill="x", padx=5, pady=5)
    
    def _on_slider_change(self, value):
        """Handle slider change."""
        self.value_label.configure(text=str(int(value)))
        self.on_change(int(value))
    
    def get(self) -> int:
        """Get current slider value."""
        return int(self.slider.get())
    
    def set(self, value: int):
        """Set slider value."""
        self.slider.set(value)


class EffectCard(ctk.CTkFrame):
    """Card component for effect/mode selection."""
    
    def __init__(
        self, 
        parent, 
        title: str,
        description: str,
        icon: str = "○",
        on_click: Optional[Callable] = None,
        selected: bool = False,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        self.title = title
        self.description = description
        self.on_click = on_click
        self.is_selected = selected
        self.configure(
            fg_color="#2b2b2b" if not selected else "#444444",
            border_width=2,
            border_color="#8a0000" if selected else "#555555",
            corner_radius=10
        )
        self._create_widgets(icon)
    
    def _create_widgets(self, icon: str):
        """Create card content."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            header,
            text=icon,
            font=("Arial", 20)
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text=self.title,
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkLabel(
            self,
            text=self.description,
            font=("Arial", 10),
            text_color="#aaa",
            wraplength=200
        ).pack(fill="x", padx=15, pady=(0, 15))
        
        if self.on_click:
            self.bind("<Button-1>", lambda e: self.on_click())
            for widget in self.winfo_children():
                widget.bind("<Button-1>", lambda e: self.on_click())
    
    def set_selected(self, selected: bool):
        """Update selected state."""
        self.is_selected = selected
        if selected:
            self.configure(
                fg_color="#444444",
                border_color="#8a0000"
            )
        else:
            self.configure(
                fg_color="#2b2b2b",
                border_color="#555555"
            )


class ToggleButton(ctk.CTkButton):
    """Toggle button that maintains on/off state."""
    
    def __init__(
        self,
        parent,
        text_on: str = "ON",
        text_off: str = "OFF",
        on_toggle: Optional[Callable[[bool], None]] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        self.text_on = text_on
        self.text_off = text_off
        self.on_toggle = on_toggle
        self.is_on = False
        self.configure(command=self._toggle)
        self._update_appearance()
    
    def _toggle(self):
        """Toggle state."""
        self.is_on = not self.is_on
        self._update_appearance()
        if self.on_toggle:
            self.on_toggle(self.is_on)
    
    def _update_appearance(self):
        """Update button appearance based on state."""
        if self.is_on:
            self.configure(
                text=self.text_on,
                fg_color="#00ff00",
                text_color="#000",
                hover_color="#00dd00"
            )
        else:
            self.configure(
                text=self.text_off,
                fg_color="#555555",
                text_color="#fff",
                hover_color="#666666"
            )
    
    def set_on(self, on: bool):
        """Set toggle state without triggering callback."""
        self.is_on = on
        self._update_appearance()


class StatPanel(ctk.CTkFrame):
    """Panel for displaying statistics and metrics."""
    
    def __init__(self, parent, title: str, **kwargs):
        super().__init__(parent, **kwargs)
        self.title = title
        self.stats: dict = {}
        ctk.CTkLabel(
            self,
            text=title,
            font=("Arial", 12, "bold"),
            text_color="#aaa"
        ).pack(anchor="w", padx=10, pady=(10, 5))
    
    def set_stat(self, key: str, value: str):
        """Update or add statistic."""
        self.stats[key] = value
        self._render_stats()
    
    def _render_stats(self):
        """Render all statistics."""
        # Clear existing stat widgets
        for widget in self.winfo_children()[1:]:  # Skip title label
            widget.destroy()
        
        for key, value in self.stats.items():
            stat_frame = ctk.CTkFrame(self, fg_color="transparent")
            stat_frame.pack(fill="x", padx=10, pady=3)
            
            ctk.CTkLabel(
                stat_frame,
                text=f"{key}:",
                font=("Arial", 10),
                text_color="#888",
                width=60
            ).pack(side="left")
            
            ctk.CTkLabel(
                stat_frame,
                text=str(value),
                font=("Courier", 10, "bold")
            ).pack(side="left", padx=5)


class DeviceDiscoveryList(ctk.CTkFrame):
    """List of discovered BLE devices with connection buttons."""
    
    def __init__(self, parent, on_select: Callable[[str, str], None], **kwargs):
        super().__init__(parent, **kwargs)
        self.on_select = on_select
        self.devices = []
        self._create_widgets()
    
    def _create_widgets(self):
        """Create device list UI."""
        header = ctk.CTkLabel(
            self,
            text="Available Devices",
            font=("Arial", 12, "bold")
        )
        header.pack(fill="x", padx=10, pady=(10, 5))
        
        # Scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    def add_device(self, name: str, mac: str, rssi: int = 0):
        """Add device to list."""
        self.devices.append({"name": name, "mac": mac, "rssi": rssi})
        self._render_device(name, mac, rssi)
    
    def _render_device(self, name: str, mac: str, rssi: int):
        """Render single device entry."""
        device_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="#2b2b2b",
            border_width=1,
            border_color="#444",
            corner_radius=8
        )
        device_frame.pack(fill="x", pady=5)
        
        info_frame = ctk.CTkFrame(device_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=name,
            font=("Arial", 11, "bold")
        ).pack(anchor="w")
        
        signal_strength = self._rssi_to_bars(rssi)
        ctk.CTkLabel(
            info_frame,
            text=f"{mac} | Signal: {signal_strength} ({rssi} dBm)",
            font=("Arial", 9),
            text_color="#888"
        ).pack(anchor="w")
        
        ctk.CTkButton(
            device_frame,
            text="Connect",
            width=80,
            command=lambda: self.on_select(name, mac)
        ).pack(side="right", padx=10, pady=10)
    
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
    
    def clear(self):
        """Clear all devices from list."""
        self.devices = []
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
