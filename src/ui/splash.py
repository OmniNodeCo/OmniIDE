"""Startup splash screen — v1.0.3."""

import tkinter as tk
import math


class SplashScreen:
    """Animated splash screen."""

    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel()
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)

        self.width = 480
        self.height = 320

        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - self.width) // 2
        y = (screen_h - self.height) // 2
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")

        try:
            self.window.attributes("-alpha", 0.0)
        except Exception:
            pass

        self.bg_color = "#1e1e2e"
        self.accent = "#89b4fa"
        self.accent2 = "#cba6f7"
        self.fg = "#cdd6f4"
        self.fg_dim = "#6c7086"

        self.canvas = tk.Canvas(
            self.window, width=self.width, height=self.height,
            bg=self.bg_color, highlightthickness=0, bd=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._rounded_rect(2, 2, self.width - 2, self.height - 2, 16, "#313244")

        cx, cy = self.width // 2, 110
        self.cx, self.cy = cx, cy

        self.canvas.create_oval(cx - 50, cy - 50, cx + 50, cy + 50, outline=self.accent, width=3)
        self.canvas.create_oval(cx - 32, cy - 32, cx + 32, cy + 32, outline=self.accent2, width=2)
        self.canvas.create_oval(cx - 6, cy - 6, cx + 6, cy + 6, fill="#f5c2e7", outline="")

        self.canvas.create_text(cx - 18, cy, text="<", font=("Consolas", 18, "bold"), fill=self.accent2)
        self.canvas.create_text(cx + 18, cy, text=">", font=("Consolas", 18, "bold"), fill=self.accent)

        self.orb_dots = []
        for _ in range(6):
            dot_id = self.canvas.create_oval(0, 0, 5, 5, fill=self.accent, outline="")
            self.orb_dots.append(dot_id)

        self.canvas.create_text(cx, cy + 70, text="OmniIDE", font=("Segoe UI", 28, "bold"), fill=self.fg)
        self.canvas.create_text(cx, cy + 95, text="by OmniNodeCo", font=("Segoe UI", 11), fill=self.fg_dim)

        self.status_text = self.canvas.create_text(
            cx, self.height - 50, text="Starting up...",
            font=("Segoe UI", 10), fill=self.fg_dim,
        )

        bar_y = self.height - 28
        bar_pad = 60
        self._rounded_rect(bar_pad, bar_y, self.width - bar_pad, bar_y + 6, 3, "#313244")
        self.progress_bar = self.canvas.create_rectangle(bar_pad, bar_y, bar_pad, bar_y + 6, fill=self.accent, outline="")
        self.bar_y = bar_y
        self.bar_pad = bar_pad
        self.bar_width = self.width - 2 * bar_pad

        self.canvas.create_text(self.width - 12, 12, text="v1.0.3", font=("Consolas", 8), fill=self.fg_dim, anchor="ne")

        self.angle = 0
        self.alpha = 0.0
        self._fade_in()
        self._animate()

    def _rounded_rect(self, x1, y1, x2, y2, r, color):
        self.canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, outline=color, style="arc")
        self.canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, outline=color, style="arc")
        self.canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, outline=color, style="arc")
        self.canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, outline=color, style="arc")
        self.canvas.create_line(x1+r, y1, x2-r, y1, fill=color)
        self.canvas.create_line(x1+r, y2, x2-r, y2, fill=color)
        self.canvas.create_line(x1, y1+r, x1, y2-r, fill=color)
        self.canvas.create_line(x2, y1+r, x2, y2-r, fill=color)

    def _fade_in(self):
        if self.alpha < 1.0:
            self.alpha += 0.06
            try:
                self.window.attributes("-alpha", min(self.alpha, 1.0))
            except Exception:
                pass
            self.window.after(16, self._fade_in)

    def _animate(self):
        try:
            if not self.window.winfo_exists():
                return
        except Exception:
            return

        self.angle += 3
        for i, dot_id in enumerate(self.orb_dots):
            offset = i * (360 / len(self.orb_dots))
            rad = math.radians(self.angle + offset)
            r = 44
            dx = self.cx + r * math.cos(rad)
            dy = self.cy + r * math.sin(rad)
            pulse = 2 + math.sin(math.radians(self.angle * 2 + offset)) * 1.5
            self.canvas.coords(dot_id, dx - pulse, dy - pulse, dx + pulse, dy + pulse)
            color = self.accent if i % 2 == 0 else self.accent2
            self.canvas.itemconfig(dot_id, fill=color)

        self.window.after(30, self._animate)

    def update_status(self, text):
        try:
            self.canvas.itemconfig(self.status_text, text=text)
            self.window.update_idletasks()
        except Exception:
            pass

    def set_progress(self, percent):
        try:
            fill_w = (percent / 100.0) * self.bar_width
            self.canvas.coords(self.progress_bar, self.bar_pad, self.bar_y, self.bar_pad + fill_w, self.bar_y + 6)
            if percent < 40:
                color = self.accent
            elif percent < 75:
                color = self.accent2
            else:
                color = "#a6e3a1"
            self.canvas.itemconfig(self.progress_bar, fill=color)
            self.window.update_idletasks()
        except Exception:
            pass

    def close(self):
        self._fade_out()

    def _fade_out(self):
        if self.alpha > 0.0:
            self.alpha -= 0.08
            try:
                self.window.attributes("-alpha", max(self.alpha, 0.0))
            except Exception:
                pass
            if self.alpha > 0:
                self.window.after(16, self._fade_out)
            else:
                try:
                    self.window.destroy()
                except Exception:
                    pass
        else:
            try:
                self.window.destroy()
            except Exception:
                pass