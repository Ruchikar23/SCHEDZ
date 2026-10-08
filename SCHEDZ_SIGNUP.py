"""
SCHEDZ - Simplified Signup System
Open-Source Project Lab Event Management
- Gradient Background: Light Blue to White
- Direct, clearly visible text entry fields
- Save / Register button with Return key support
- Zero external database setup (built-in SQLite)
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import os

from db_manager import register_user, init_db
from ui_theme import (
    COLORS, FONTS, apply_window_decorations,
    draw_light_gradient
)

init_db()


class SignupApp:
    def __init__(self, root):
        self.root = root
        apply_window_decorations(self.root, "S C H E D Z - Signup")
        self.root.geometry("540x680")
        self.root.minsize(500, 640)

        # 1. Gradient Canvas Background (Light Blue to White)
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.root.bind("<Configure>", self.on_window_resize)

        # 2. Signup Card
        self.create_signup_card()

    def on_window_resize(self, event):
        """Redraws light blue to white gradient upon resize."""
        if event.widget == self.root:
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            draw_light_gradient(self.canvas, w, h, color1=COLORS["gradient_start"], color2=COLORS["gradient_end"])

    def create_signup_card(self):
        # White center frame
        self.card = tk.Frame(
            self.canvas,
            bg=COLORS["card_bg"],
            relief="solid",
            bd=1,
            padx=32,
            pady=24
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        tk.Label(
            self.card,
            text="Create New Account",
            bg=COLORS["card_bg"],
            fg=COLORS["primary"],
            font=FONTS["title_large"]
        ).pack(pady=(0, 2))

        tk.Label(
            self.card,
            text="Register to manage or view schedules",
            bg=COLORS["card_bg"],
            fg=COLORS["text_muted"],
            font=FONTS["body"]
        ).pack(pady=(0, 16))

        # 1. Username
        tk.Label(self.card, text="Username / Name * (Max 20 chars)", bg=COLORS["card_bg"], fg=COLORS["text_dark"], font=FONTS["body_bold"], anchor="w").pack(fill="x", pady=(3, 1))
        self.username_entry = tk.Entry(self.card, font=FONTS["body"], bg=COLORS["input_bg"], fg=COLORS["text_dark"], relief="solid", bd=1, width=30)
        self.username_entry.pack(fill="x", pady=(0, 8), ipady=4)

        # 2. Email
        tk.Label(self.card, text="Email Address * (Must be @gmail.com)", bg=COLORS["card_bg"], fg=COLORS["text_dark"], font=FONTS["body_bold"], anchor="w").pack(fill="x", pady=(3, 1))
        self.email_entry = tk.Entry(self.card, font=FONTS["body"], bg=COLORS["input_bg"], fg=COLORS["text_dark"], relief="solid", bd=1, width=30)
        self.email_entry.pack(fill="x", pady=(0, 8), ipady=4)

        # 3. Phone Number
        tk.Label(self.card, text="Phone Number * (Exactly 10 digits)", bg=COLORS["card_bg"], fg=COLORS["text_dark"], font=FONTS["body_bold"], anchor="w").pack(fill="x", pady=(3, 1))
        self.phone_entry = tk.Entry(self.card, font=FONTS["body"], bg=COLORS["input_bg"], fg=COLORS["text_dark"], relief="solid", bd=1, width=30)
        self.phone_entry.pack(fill="x", pady=(0, 8), ipady=4)

        # 4. Password
        tk.Label(self.card, text="Password *", bg=COLORS["card_bg"], fg=COLORS["text_dark"], font=FONTS["body_bold"], anchor="w").pack(fill="x", pady=(3, 1))
        self.password_entry = tk.Entry(self.card, show="*", font=FONTS["body"], bg=COLORS["input_bg"], fg=COLORS["text_dark"], relief="solid", bd=1, width=30)
        self.password_entry.pack(fill="x", pady=(0, 8), ipady=4)

        # 5. User Type (Role)
        tk.Label(self.card, text="User Role *", bg=COLORS["card_bg"], fg=COLORS["text_dark"], font=FONTS["body_bold"], anchor="w").pack(fill="x", pady=(3, 1))
        self.menu_var = tk.StringVar(value="Student")
        self.role_menu = tk.OptionMenu(self.card, self.menu_var, "Admin", "Committee", "Student")
        self.role_menu.config(bg="#E0F2FE", fg=COLORS["primary"], font=FONTS["body"], relief="flat", anchor="w")
        self.role_menu.pack(fill="x", pady=(0, 8))

        # 6. Department Selection (Radio Buttons)
        tk.Label(self.card, text="Department *", bg=COLORS["card_bg"], fg=COLORS["text_dark"], font=FONTS["body_bold"], anchor="w").pack(fill="x", pady=(3, 2))
        self.dept_var = tk.StringVar(value="College")
        dept_frame = tk.Frame(self.card, bg=COLORS["card_bg"])
        dept_frame.pack(fill="x", pady=(0, 16))

        tk.Radiobutton(
            dept_frame, text="College", variable=self.dept_var, value="College",
            bg=COLORS["card_bg"], fg=COLORS["text_dark"], font=FONTS["body"]
        ).pack(side="left", padx=(0, 20))

        tk.Radiobutton(
            dept_frame, text="School", variable=self.dept_var, value="School",
            bg=COLORS["card_bg"], fg=COLORS["text_dark"], font=FONTS["body"]
        ).pack(side="left")

        # 7. SAVE / REGISTER BUTTON
        self.save_btn = tk.Button(
            self.card,
            text="Save / Register User",
            command=self.save_user,
            bg=COLORS["primary"],
            fg="#FFFFFF",
            activebackground=COLORS["primary_hover"],
            activeforeground="#FFFFFF",
            font=FONTS["body_bold"],
            relief="flat",
            cursor="hand2",
            pady=8
        )
        self.save_btn.pack(fill="x", pady=(0, 8))

        # 8. Back to Login Button
        self.back_btn = tk.Button(
            self.card,
            text="Back to Login",
            command=self.root.destroy,
            bg="#F1F5F9",
            fg=COLORS["text_muted"],
            activebackground="#E2E8F0",
            font=FONTS["body"],
            relief="flat",
            cursor="hand2",
            pady=6
        )
        self.back_btn.pack(fill="x")

        # Bind Return key
        self.root.bind("<Return>", lambda e: self.save_user())
        self.username_entry.focus_set()

    def save_user(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        password = self.password_entry.get().strip()
        user_type = self.menu_var.get().strip()
        department = self.dept_var.get().strip()

        # 1. All fields required
        if not username:
            messagebox.showerror("Validation Error", "Please fill in Username / Name! All fields are required.")
            self.username_entry.focus_set()
            return

        if not email:
            messagebox.showerror("Validation Error", "Please fill in Email Address! All fields are required.")
            self.email_entry.focus_set()
            return

        if not phone:
            messagebox.showerror("Validation Error", "Please fill in Phone Number! All fields are required.")
            self.phone_entry.focus_set()
            return

        if not password:
            messagebox.showerror("Validation Error", "Please fill in Password! All fields are required.")
            self.password_entry.focus_set()
            return

        if not user_type or user_type == "Select User Type":
            messagebox.showerror("Validation Error", "Please select a User Role! All fields are required.")
            return

        if not department:
            messagebox.showerror("Validation Error", "Please select a Department! All fields are required.")
            return

        # 2. Maximum 20 characters for name
        if len(username) > 20:
            messagebox.showerror(
                "Validation Error",
                f"Username / Name cannot exceed 20 characters!\n(Current length: {len(username)} characters)"
            )
            self.username_entry.focus_set()
            return

        # 3. Exactly 10 digits for phone number
        if not (phone.isdigit() and len(phone) == 10):
            messagebox.showerror(
                "Validation Error",
                "Phone number must contain exactly 10 numeric digits!\n(Example: 9876543210)"
            )
            self.phone_entry.focus_set()
            return

        # 4. Email must contain @gmail.com
        email_lower = email.lower()
        if not (email_lower.endswith("@gmail.com") and len(email_lower) > len("@gmail.com")):
            messagebox.showerror(
                "Validation Error",
                "Email must be in a valid format ending with @gmail.com!\n(Example: student@gmail.com)"
            )
            self.email_entry.focus_set()
            return

        success, msg = register_user(username, email, phone, password, user_type, department)
        if success:
            messagebox.showinfo("Success", "User registered successfully!\nYou can now log in.")
            self.root.destroy()
        else:
            messagebox.showerror("Registration Error", msg)


def main():
    root = tk.Tk()
    app = SignupApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
