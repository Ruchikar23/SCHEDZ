"""
SCHEDZ - Simplified Login System
Open-Source Project Lab Event Management
- Gradient Background: Light Blue to White
- Direct, visible text entry fields for Username and Password
- Enter / Login button with Return key support
- Zero SQL setup (built-in SQLite)
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

from db_manager import authenticate_user, init_db
from ui_theme import (
    COLORS, FONTS, apply_window_decorations,
    draw_light_gradient
)

# Ensure database is ready
init_db()


class LoginApp:
    def __init__(self, root):
        self.root = root
        apply_window_decorations(self.root, "S C H E D Z - Login")
        self.root.geometry("520x620")
        self.root.minsize(480, 560)

        # 1. Light Blue to White Gradient Canvas Background
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.root.bind("<Configure>", self.on_window_resize)

        # 2. Main Login Card
        self.create_login_card()

    def on_window_resize(self, event):
        """Redraws the light blue to white gradient when window size changes."""
        if event.widget == self.root:
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            draw_light_gradient(self.canvas, w, h, color1=COLORS["gradient_start"], color2=COLORS["gradient_end"])

    def create_login_card(self):
        # White center frame with clean border
        self.card = tk.Frame(
            self.canvas,
            bg=COLORS["card_bg"],
            relief="solid",
            bd=1,
            padx=32,
            pady=28
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        # Title: S C H E D Z
        title_label = tk.Label(
            self.card,
            text="S C H E D Z",
            bg=COLORS["card_bg"],
            fg=COLORS["primary"],
            font=FONTS["title_large"]
        )
        title_label.pack(pady=(0, 2))

        # Tagline
        subtitle_label = tk.Label(
            self.card,
            text="Plan, Organize, Achieve",
            bg=COLORS["card_bg"],
            fg=COLORS["text_muted"],
            font=FONTS["subtitle"]
        )
        subtitle_label.pack(pady=(0, 18))

        # ----------------- USERNAME INPUT -----------------
        lbl_user = tk.Label(
            self.card,
            text="Username:",
            bg=COLORS["card_bg"],
            fg=COLORS["text_dark"],
            font=FONTS["body_bold"],
            anchor="w"
        )
        lbl_user.pack(fill="x", pady=(5, 2))

        # Direct, clearly visible Entry box
        self.username_entry = tk.Entry(
            self.card,
            font=FONTS["body"],
            bg=COLORS["input_bg"],
            fg=COLORS["text_dark"],
            relief="solid",
            bd=1,
            width=28
        )
        self.username_entry.pack(fill="x", pady=(0, 10), ipady=5)

        # ----------------- PASSWORD INPUT -----------------
        lbl_pass = tk.Label(
            self.card,
            text="Password:",
            bg=COLORS["card_bg"],
            fg=COLORS["text_dark"],
            font=FONTS["body_bold"],
            anchor="w"
        )
        lbl_pass.pack(fill="x", pady=(5, 2))

        # Direct, clearly visible Entry box
        self.password_entry = tk.Entry(
            self.card,
            show="*",
            font=FONTS["body"],
            bg=COLORS["input_bg"],
            fg=COLORS["text_dark"],
            relief="solid",
            bd=1,
            width=28
        )
        self.password_entry.pack(fill="x", pady=(0, 8), ipady=5)

        # Show / Hide Password Checkbox
        self.show_pass_var = tk.BooleanVar(value=False)
        chk_pass = tk.Checkbutton(
            self.card,
            text="Show Password",
            variable=self.show_pass_var,
            command=self.toggle_password,
            bg=COLORS["card_bg"],
            fg=COLORS["text_muted"],
            activebackground=COLORS["card_bg"],
            font=FONTS["small"]
        )
        chk_pass.pack(anchor="w", pady=(0, 16))

        # ----------------- ENTER / LOGIN BUTTON -----------------
        self.login_btn = tk.Button(
            self.card,
            text="Enter / Login",
            command=self.handle_login,
            bg=COLORS["primary"],
            fg="#FFFFFF",
            activebackground=COLORS["primary_hover"],
            activeforeground="#FFFFFF",
            font=FONTS["body_bold"],
            relief="flat",
            cursor="hand2",
            pady=8
        )
        self.login_btn.pack(fill="x", pady=(0, 8))

        # ----------------- SIGN UP BUTTON -----------------
        self.signup_btn = tk.Button(
            self.card,
            text="Don't have an account? Sign Up",
            command=self.open_signup,
            bg="#F1F5F9",
            fg=COLORS["primary"],
            activebackground="#E2E8F0",
            activeforeground=COLORS["primary"],
            font=FONTS["body"],
            relief="flat",
            cursor="hand2",
            pady=6
        )
        self.signup_btn.pack(fill="x", pady=(0, 15))

        # ----------------- QUICK DEMO BUTTONS -----------------
        demo_frame = tk.LabelFrame(
            self.card,
            text="Quick Demo Fill",
            bg=COLORS["card_bg"],
            fg=COLORS["text_muted"],
            font=FONTS["small"],
            padx=8,
            pady=6
        )
        demo_frame.pack(fill="x")

        roles = [
            ("Admin", "admin", "admin123"),
            ("Committee", "committee", "comm123"),
            ("Student", "student", "stud123")
        ]
        for role_name, u, p in roles:
            b = tk.Button(
                demo_frame,
                text=role_name,
                command=lambda un=u, pw=p: self.fill_credentials(un, pw),
                bg="#E0F2FE",
                fg=COLORS["primary"],
                relief="flat",
                font=FONTS["small"],
                cursor="hand2",
                padx=6,
                pady=2
            )
            b.pack(side="left", expand=True, fill="x", padx=2)

        # Pressing Enter on keyboard triggers Enter / Login
        self.root.bind("<Return>", lambda e: self.handle_login())

        # Set default focus on username
        self.username_entry.focus_set()

    def toggle_password(self):
        """Toggles between hidden '*' and clear text password."""
        if self.show_pass_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def fill_credentials(self, username, password):
        """Fills entry fields for easy 1-click testing."""
        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, username)
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

    def handle_login(self):
        """Validates credentials and launches homepage."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in both Username and Password!")
            return

        success, user_data, msg = authenticate_user(username, password)
        if success:
            user_type = user_data["User_type"]
            username_val = user_data["Username"]
            messagebox.showinfo("Success", f"Welcome {username_val}!\nRole: {user_type}")

            # Close Login window
            self.root.destroy()

            # Launch Homepage
            homepage_path = os.path.join(os.path.dirname(__file__), "SCHEDZ_HOMEPAGE.py")
            subprocess.run([sys.executable, homepage_path, user_type, username_val])
        else:
            messagebox.showerror("Login Failed", msg)

    def open_signup(self):
        """Opens the Signup window."""
        signup_path = os.path.join(os.path.dirname(__file__), "SCHEDZ_SIGNUP.py")
        subprocess.Popen([sys.executable, signup_path])


def main():
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
