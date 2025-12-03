"""
Reusable UI component library for consistent, modern interface.
Implements design system with custom widgets built on customtkinter.
"""

import customtkinter as ctk
from typing import Callable, Optional, Tuple, List
from enum import Enum
import math


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


class ColorWheelPicker(ctk.CTkCanvas):
    """Interactive HSV color wheel for intuitive color selection."""
    
    def __init__(self, parent, size: int = 300, on_color_change: Optional[Callable] = None, **kwargs):
        """
        Create interactive color wheel.
        
        Args:
            parent: Parent widget
            size: Canvas size (width=height)
            on_color_change: Callback(r, g, b) when color selected
        """
        super().__init__(parent, width=size, height=size, bg="#1a1a1a", highlightthickness=0, **kwargs)
        self.size = size
        self.radius = size // 2 - 10
        self.center = (size // 2, size // 2)
        self.on_color_change = on_color_change
        self.selected_hue = 0
        self.selected_saturation = 0.5
        self.selected_value = 1.0
        self.picker_circle_radius = 8
        
        # Bind events
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<MouseWheel>", self._on_wheel)  # Windows
        self.bind("<Button-4>", self._on_wheel)    # Linux
        self.bind("<Button-5>", self._on_wheel)    # Linux
        
        self._draw_wheel()
    
    def _on_click(self, event):
        """Handle color wheel click."""
        self._update_from_position(event.x, event.y)
    
    def _on_drag(self, event):
        """Handle color wheel drag."""
        self._update_from_position(event.x, event.y)
    
    def _on_wheel(self, event):
        """Handle mouse wheel for brightness adjustment."""
        if event.num == 5 or event.delta < 0:
            self.selected_value = max(0.1, self.selected_value - 0.1)
        else:
            self.selected_value = min(1.0, self.selected_value + 0.1)
        self._draw_wheel()
        self._emit_color()
    
    def _update_from_position(self, x: int, y: int):
        """Convert click position to HSV and update color."""
        # Calculate distance from center
        dx = x - self.center[0]
        dy = y - self.center[1]
        dist = math.sqrt(dx**2 + dy**2)
        
        # Clamp to wheel radius
        if dist > self.radius:
            dist = self.radius
        
        # Calculate hue (angle)
        angle = math.atan2(dy, dx) * 180 / math.pi
        self.selected_hue = (angle + 90) % 360
        
        # Calculate saturation (distance from center)
        self.selected_saturation = max(0.0, min(1.0, dist / self.radius))
        
        self._draw_wheel()
        self._emit_color()
    
    def _emit_color(self):
        """Convert HSV to RGB and emit callback."""
        if self.on_color_change:
            r, g, b = self._hsv_to_rgb(self.selected_hue, self.selected_saturation, self.selected_value)
            self.on_color_change(int(r), int(g), int(b))
    
    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[float, float, float]:
        """Convert HSV to RGB."""
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        return ((r + m) * 255, (g + m) * 255, (b + m) * 255)
    
    def _rgb_to_hsv(self, r: float, g: float, b: float) -> Tuple[float, float, float]:
        """Convert RGB (0-255) to HSV."""
        r, g, b = r / 255, g / 255, b / 255
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        delta = max_c - min_c
        
        if delta == 0:
            h = 0
        elif max_c == r:
            h = (60 * ((g - b) / delta) + 360) % 360
        elif max_c == g:
            h = (60 * ((b - r) / delta) + 120) % 360
        else:
            h = (60 * ((r - g) / delta) + 240) % 360
        
        s = 0 if max_c == 0 else delta / max_c
        v = max_c
        
        return h, s, v
    
    def set_color(self, r: int, g: int, b: int):
        """Set color from RGB values."""
        h, s, v = self._rgb_to_hsv(r, g, b)
        self.selected_hue = h
        self.selected_saturation = s
        self.selected_value = v
        self._draw_wheel()
    
    def _draw_wheel(self):
        """Draw the color wheel with gradient."""
        self.delete("all")
        
        # Draw color wheel segments
        segments = 360
        for i in range(segments):
            angle1 = i
            angle2 = i + 1
            r1, g1, b1 = self._hsv_to_rgb(angle1, 1.0, self.selected_value)
            hex_color = f"#{int(r1):02x}{int(g1):02x}{int(b1):02x}"
            
            # Draw arc segment
            self._draw_arc_segment(angle1, angle2, hex_color)
        
        # Draw selected position marker
        if self.selected_saturation > 0 or self.selected_value > 0:
            angle_rad = (self.selected_hue - 90) * math.pi / 180
            x = self.center[0] + self.selected_saturation * self.radius * math.cos(angle_rad)
            y = self.center[1] + self.selected_saturation * self.radius * math.sin(angle_rad)
            
            self.create_oval(
                x - self.picker_circle_radius - 2, y - self.picker_circle_radius - 2,
                x + self.picker_circle_radius + 2, y + self.picker_circle_radius + 2,
                outline="white", width=2
            )
            self.create_oval(
                x - self.picker_circle_radius, y - self.picker_circle_radius,
                x + self.picker_circle_radius, y + self.picker_circle_radius,
                outline="black", width=1
            )
        
        # Draw center circle (value control)
        value_color = f"#{int(self.selected_value * 255):02x}{int(self.selected_value * 255):02x}{int(self.selected_value * 255):02x}"
        self.create_oval(
            self.center[0] - 20, self.center[1] - 20,
            self.center[0] + 20, self.center[1] + 20,
            fill=value_color, outline="white", width=2
        )
        self.create_text(
            self.center[0], self.center[1] + 35,
            text=f"V: {int(self.selected_value * 100)}%",
            fill="white", font=("Arial", 10)
        )
    
    def _draw_arc_segment(self, angle1: float, angle2: float, color: str):
        """Draw a segment of the color wheel."""
        # Draw from center to edge
        angle1_rad = (angle1 - 90) * math.pi / 180
        angle2_rad = (angle2 - 90) * math.pi / 180
        
        x1 = self.center[0] + self.radius * math.cos(angle1_rad)
        y1 = self.center[1] + self.radius * math.sin(angle1_rad)
        x2 = self.center[0] + self.radius * math.cos(angle2_rad)
        y2 = self.center[1] + self.radius * math.sin(angle2_rad)
        
        # Draw triangle from center to arc
        self.create_polygon(
            self.center[0], self.center[1],
            x1, y1,
            x2, y2,
            fill=color, outline=color
        )
