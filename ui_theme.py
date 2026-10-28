"""
SCHEDZ - Simplified UI Theme
Light Blue to White gradient background with clean, professional styling.
Easy to understand for open-source lab project demonstrations.
"""

import tkinter as tk
from tkinter import ttk
import os

# Clean, simplified color palette
COLORS = {
    "gradient_start": "#CBE7F6",  # Soft Light Blue
    "primary": "#0284C7",         # Friendly Royal/Sky Blue
    "primary_hover": "#0369A1",   # Darker Blue on hover
    "secondary": "#0D9488",       # Teal accent
    "card_bg": "#FFFFFF",         # Pure White card
    "text_dark": "#0F172A",       # Dark Slate for high contrast text
    "text_muted": "#475569",      # Slate 600 for subtitles/labels
    "input_bg": "#F8FAFC",        # Soft light gray for text fields
    "border": "#CBD5E1",          # Light border
    "danger": "#DC2626",          # Clean Red
    "table_header": "#E0F2FE",    # Light blue header
}

FONTS = {
    "title_large": ("Segoe UI", 18, "bold"),
    "title": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
}


def draw_light_gradient(canvas, width, height, color1="#BAE6FD", color2="#FFFFFF"):
    """
    Renders a smooth vertical gradient from Light Blue to White.
    Pure Canvas drawing: zero external image files required.
    """
    canvas.delete("gradient_lines")

    # Hex to RGB helper
    def hex_to_rgb(hex_str):
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)

    steps = 40
    step_height = height / steps

    for i in range(steps):
        factor = i / steps
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        color = f"#{r:02x}{g:02x}{b:02x}"

        y0 = int(i * step_height)
        y1 = int((i + 1) * step_height) + 1
        canvas.create_rectangle(
            0, y0, width, y1,
            fill=color,
            outline=color,
        )
    canvas.tag_lower("gradient_lines")


def apply_window_decorations(window, title="SCHEDZ"):
    """Configures window properties cleanly and safely."""
    window.title(title)
    window.configure(bg="#F0F9FF")

    # Safe icon load
    for icon in ["schedz_icon.ico", r"c:\Python Projects\schedz_icon.ico", r"C:\Images\favicon.ico"]:
        if os.path.exists(icon):
            try:
                window.iconbitmap(icon)
                break
            except Exception:
                pass


def setup_ttk_theme():
    """Simple, clean ttk styling for tables and tabs with light colors."""
    style = ttk.Style()
    style.theme_use("clam")

    # Clean Treeview (Table)
    style.configure(
        "Treeview",
        background="#FFFFFF",
        foreground="#0F172A",
        fieldbackground="#FFFFFF",
        rowheight=28,
        font=FONTS["body"],
        borderwidth=1,
        relief="solid"
    )
    style.configure(
        "Treeview.Heading",
        background="#BAE6FD",
        foreground="#0F172A",
        font=FONTS["body_bold"],
        padding=6
    )
    style.map(
        "Treeview",
        background=[("selected", "#0284C7")],
        foreground=[("selected", "#FFFFFF")]
    )

    # Clean Tabs
    style.configure(
        "TNotebook",
        background="#F0F9FF",
        borderwidth=0
    )
    style.configure(
        "TNotebook.Tab",
        foreground="#334155",
        font=FONTS["body_bold"],
        padding=[14, 6]
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", "#0284C7")],
        foreground=[("selected", "#FFFFFF")]
    )

    return style
