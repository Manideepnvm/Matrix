# core/ui_manager.py

import tkinter as tk
from tkinter import Canvas
import threading
import time
from typing import Optional
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import math

from core.logger import log_info, log_error


class MatrixUI:
    """Modern transparent UI with animated logo and status indicators"""
    
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.canvas: Optional[Canvas] = None
        self.running = False
        
        # UI State
        self.state = "idle"
        self.current_command = ""
        self.animation_frame = 0
        
        # Colors
        self.colors = {
            'idle': '#00FFFF',      # Cyan
            'listening': '#00FF00',  # Green
            'processing': '#FFFF00', # Yellow
            'speaking': '#FF00FF',   # Magenta
            'error': '#FF0000'       # Red
        }
        
        # Animation
        self.pulse_scale = 1.0
        self.pulse_direction = 1
        self.rotation = 0
        
        log_info("UI Manager initialized")

    def run(self):
        """Run UI in its own thread"""
        try:
            self.running = True
            self._create_window()
            self._start_animation_loop()
            self.root.mainloop()
        except Exception as e:
            log_error(f"UI Error: {e}")

    def _create_window(self):
        """Create transparent overlay window"""
        self.root = tk.Tk()
        self.root.title("Matrix Voice Assistant")
        
        # Window configuration
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        window_width = 400
        window_height = 400
        x = screen_width - window_width - 50
        y = 50
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Make window transparent and always on top
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.9)
        self.root.overrideredirect(True)  # Remove window decorations
        
        # For Windows - make background transparent
        try:
            self.root.wm_attributes('-transparentcolor', 'black')
        except:
            pass
        
        # Create canvas
        self.canvas = Canvas(
            self.root,
            width=window_width,
            height=window_height,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Enable dragging
        self.canvas.bind('<Button-1>', self._on_drag_start)
        self.canvas.bind('<B1-Motion>', self._on_drag_motion)
        
        # Create UI elements
        self._create_logo()
        self._create_status_text()
        self._create_command_display()
        
        log_info("UI window created")

    def _create_logo(self):
        """Create animated Matrix logo"""
        # Create circular logo with glow effect
        center_x, center_y = 200, 150
        radius = 60
        
        # Outer glow
        self.glow_circle = self.canvas.create_oval(
            center_x - radius - 10, center_y - radius - 10,
            center_x + radius + 10, center_y + radius + 10,
            outline=self.colors['idle'],
            width=2,
            dash=(5, 5)
        )
        
        # Main circle
        self.main_circle = self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline=self.colors['idle'],
            width=3
        )
        
        # Inner design - Matrix "M"
        self.logo_text = self.canvas.create_text(
            center_x, center_y,
            text="M",
            font=("Arial", 48, "bold"),
            fill=self.colors['idle']
        )
        
        # Rotating rings
        self.ring1 = self.canvas.create_oval(
            center_x - 40, center_y - 40,
            center_x + 40, center_y + 40,
            outline=self.colors['idle'],
            width=1
        )
        
        self.ring2 = self.canvas.create_oval(
            center_x - 50, center_y - 50,
            center_x + 50, center_y + 50,
            outline=self.colors['idle'],
            width=1,
            dash=(3, 3)
        )

    def _create_status_text(self):
        """Create status indicator text"""
        self.status_text = self.canvas.create_text(
            200, 240,
            text="STANDBY",
            font=("Arial", 16, "bold"),
            fill=self.colors['idle']
        )
        
        # Status dots
        self.status_dots = []
        for i in range(3):
            dot = self.canvas.create_oval(
                170 + i * 20, 260,
                180 + i * 20, 270,
                fill=self.colors['idle'],
                outline=""
            )
            self.status_dots.append(dot)

    def _create_command_display(self):
        """Create command display area"""
        self.command_text = self.canvas.create_text(
            200, 300,
            text="",
            font=("Arial", 12),
            fill=self.colors['idle'],
            width=350
        )
        
        # Command box
        self.command_box = self.canvas.create_rectangle(
            30, 280, 370, 320,
            outline=self.colors['idle'],
            width=1,
            dash=(2, 2)
        )

    def _start_animation_loop(self):
        """Start animation update loop"""
        self._animate()

    def _animate(self):
        """Main animation loop"""
        if not self.running or not self.root:
            return
        
        try:
            # Update animation frame
            self.animation_frame += 1
            
            # Pulse effect
            self.pulse_scale += 0.02 * self.pulse_direction
            if self.pulse_scale > 1.1:
                self.pulse_direction = -1
            elif self.pulse_scale < 0.9:
                self.pulse_direction = 1
            
            # Rotation effect
            self.rotation = (self.rotation + 2) % 360
            
            # Update visuals based on state
            self._update_pulse()
            self._update_rotation()
            self._update_status_dots()
            
            # Schedule next frame
            self.root.after(50, self._animate)
            
        except Exception as e:
            log_error(f"Animation error: {e}")

    def _update_pulse(self):
        """Update pulsing animation"""
        try:
            current_color = self.colors.get(self.state, self.colors['idle'])
            
            # Update colors with pulse
            alpha = int(255 * self.pulse_scale)
            
            self.canvas.itemconfig(self.glow_circle, outline=current_color)
            self.canvas.itemconfig(self.main_circle, outline=current_color)
            self.canvas.itemconfig(self.logo_text, fill=current_color)
            self.canvas.itemconfig(self.ring1, outline=current_color)
            self.canvas.itemconfig(self.ring2, outline=current_color)
            
        except Exception as e:
            log_error(f"Pulse update error: {e}")

    def _update_rotation(self):
        """Update rotating elements"""
        # Rotate rings by changing dash offset
        try:
            dash_offset = int(self.rotation / 10)
            self.canvas.itemconfig(self.ring2, dashoffset=dash_offset)
        except:
            pass

    def _update_status_dots(self):
        """Animate status indicator dots"""
        try:
            for i, dot in enumerate(self.status_dots):
                frame_offset = (self.animation_frame + i * 10) % 30
                if frame_offset < 15:
                    self.canvas.itemconfig(dot, fill=self.colors.get(self.state, self.colors['idle']))
                else:
                    self.canvas.itemconfig(dot, fill='')
        except:
            pass

    def update_state(self, new_state: str):
        """Update UI state"""
        self.state = new_state.lower()
        
        state_labels = {
            'idle': 'STANDBY',
            'listening': 'LISTENING',
            'processing': 'PROCESSING',
            'speaking': 'SPEAKING',
            'wake_word_detection': 'MONITORING',
            'error': 'ERROR'
        }
        
        label = state_labels.get(self.state, 'UNKNOWN')
        
        if self.root:
            self.root.after(0, lambda: self._update_state_ui(label))

    def _update_state_ui(self, label: str):
        """Update state UI elements"""
        try:
            self.canvas.itemconfig(self.status_text, text=label)
            current_color = self.colors.get(self.state, self.colors['idle'])
            self.canvas.itemconfig(self.status_text, fill=current_color)
        except:
            pass

    def show_command(self, command: str):
        """Display current command"""
        self.current_command = command
        if self.root:
            self.root.after(0, lambda: self._update_command_ui(command))

    def _update_command_ui(self, command: str):
        """Update command display"""
        try:
            display_text = command[:50] + "..." if len(command) > 50 else command
            self.canvas.itemconfig(self.command_text, text=display_text)
        except:
            pass

    def trigger_activation(self):
        """Trigger activation animation"""
        if self.root:
            self.root.after(0, self._activation_flash)

    def _activation_flash(self):
        """Flash effect on activation"""
        try:
            original_alpha = self.root.attributes('-alpha')
            self.root.attributes('-alpha', 1.0)
            self.root.after(100, lambda: self.root.attributes('-alpha', original_alpha))
        except:
            pass

    def trigger_deactivation(self):
        """Trigger deactivation animation"""
        pass  # Implement fade out effect if needed

    def _on_drag_start(self, event):
        """Handle drag start"""
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag_motion(self, event):
        """Handle drag motion"""
        try:
            x = self.root.winfo_x() + event.x - self._drag_x
            y = self.root.winfo_y() + event.y - self._drag_y
            self.root.geometry(f"+{x}+{y}")
        except:
            pass

    def close(self):
        """Close UI"""
        self.running = False
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
        log_info("UI closed")


# Alias for backward compatibility
UIManager = MatrixUI