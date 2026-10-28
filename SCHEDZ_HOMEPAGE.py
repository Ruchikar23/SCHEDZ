"""
SCHEDZ - Simplified Homepage
Open-Source Project Lab Event Management
- Gradient Background: Light Blue to White
- Direct, visible text entry fields throughout all forms
- Clear Save / Enter buttons on all forms
- Enhanced Notes Workspace with immediate live reflection upon saving
- Role-based controls (Admin, Committee, Student)
- (Overview tab completely removed as requested)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import sys
import os
import subprocess
from datetime import datetime

from db_manager import (
    get_schedules, add_schedule, delete_schedule,
    get_showflow, add_showflow_item, delete_showflow_item,
    get_notes, add_note, update_note, delete_note,
    init_db
)
from ui_theme import (
    COLORS, FONTS, apply_window_decorations, setup_ttk_theme,
    draw_light_gradient
)

init_db()


class SchedzHomepage:
    def __init__(self, root, user_type="Admin", username="admin"):
        self.root = root
        self.user_type = user_type if user_type else "Admin"
        self.username = username if username else "admin"

        apply_window_decorations(self.root, f"S C H E D Z - Homepage ({self.user_type})")
        self.root.geometry("1020x720")
        self.root.minsize(900, 640)

        setup_ttk_theme()

        # Canvas with light blue to white gradient
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.root.bind("<Configure>", self.on_window_resize)

        # State for notes
        self.current_selected_note_id = None
        self.notes_data = []
        self._auto_save_timer = None
        self._is_auto_saving = False

        # Build clean header and tabs
        self.build_header()
        self.build_tabs()
        self.build_statusbar()

    def on_window_resize(self, event):
        if event.widget == self.root:
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            draw_light_gradient(self.canvas, w, h, color1=COLORS["gradient_start"], color2=COLORS["gradient_end"])

    def build_header(self):
        """Top banner with system title and user badge."""
        header = tk.Frame(self.canvas, bg="#0284C7", padx=20, pady=12)
        header.pack(fill="x", side="top")

        # Left: Title and Tagline
        left_box = tk.Frame(header, bg="#0284C7")
        left_box.pack(side="left")

        tk.Label(
            left_box,
            text="S C H E D Z",
            font=("Segoe UI", 18, "bold"),
            fg="#FFFFFF",
            bg="#0284C7"
        ).pack(anchor="w")

        tk.Label(
            left_box,
            text="Planning made simple! • Open-Source Project Lab",
            font=("Segoe UI", 10),
            fg="#E0F2FE",
            bg="#0284C7"
        ).pack(anchor="w")

        # Right: User info & logout
        right_box = tk.Frame(header, bg="#0284C7")
        right_box.pack(side="right")

        tk.Label(
            right_box,
            text=f"User: {self.username} | Role: {self.user_type}",
            font=FONTS["body_bold"],
            fg="#FFFFFF",
            bg="#0369A1",
            padx=10,
            pady=4
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            right_box,
            text="Sign Out",
            command=self.logout,
            bg="#FFFFFF",
            fg="#0284C7",
            font=FONTS["small"],
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=3
        ).pack(side="left")

    def build_tabs(self):
        """Tabbed navigation for simple switching between features (No Overview tab)."""
        tab_container = tk.Frame(self.canvas, bg="#FFFFFF", relief="solid", bd=1)
        tab_container.pack(fill="both", expand=True, padx=16, pady=(12, 6))

        self.notebook = ttk.Notebook(tab_container)
        self.notebook.pack(fill="both", expand=True, padx=6, pady=6)

        # Tab 1: View Schedules
        self.tab_schedules = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_schedules, text=" View Schedules ")
        self.build_schedules_tab()

        # Tab 2: Add Schedule (Admin & Committee only)
        if self.user_type in ["Admin", "Committee"]:
            self.tab_add_sched = tk.Frame(self.notebook, bg="#FFFFFF")
            self.notebook.add(self.tab_add_sched, text=" Add Schedule ")
            self.build_add_schedule_tab()

        # Tab 3: Showflow (Itinerary)
        self.tab_showflow = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_showflow, text=" Showflow ")
        self.build_showflow_tab()

        # Tab 4: Notes (Enhanced Workspace)
        self.tab_notes = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_notes, text=" Notes ")
        self.build_notes_tab()

    # ---------------------------------------------------------
    # TAB 1: VIEW SCHEDULES
    # ---------------------------------------------------------
    def build_schedules_tab(self):
        filter_bar = tk.Frame(self.tab_schedules, bg="#F0F9FF", padx=10, pady=8, relief="solid", bd=1)
        filter_bar.pack(fill="x", padx=10, pady=(10, 8))

        # Search Label & Entry Box
        tk.Label(filter_bar, text="Search Event:", font=FONTS["body_bold"], bg="#F0F9FF", fg="#0F172A").pack(side="left", padx=(0, 5))
        self.search_entry = tk.Entry(filter_bar, font=FONTS["body"], bg="#FFFFFF", fg="#0F172A", relief="solid", bd=1, width=20)
        self.search_entry.pack(side="left", padx=(0, 12), ipady=3)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_schedules())

        # Department Filter
        tk.Label(filter_bar, text="Department:", font=FONTS["body_bold"], bg="#F0F9FF", fg="#0F172A").pack(side="left", padx=(0, 5))
        self.dept_filter_var = tk.StringVar(value="All")
        dept_combo = ttk.Combobox(filter_bar, textvariable=self.dept_filter_var, values=["All", "College", "School"], state="readonly", width=10)
        dept_combo.pack(side="left", padx=(0, 12))
        dept_combo.bind("<<ComboboxSelected>>", lambda e: self.load_schedules())

        # Enter / Search Button
        tk.Button(
            filter_bar,
            text="Enter / Search",
            command=self.load_schedules,
            bg="#0284C7",
            fg="#FFFFFF",
            font=FONTS["small"],
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=3
        ).pack(side="left", padx=3)

        # Admin: Delete Button
        if self.user_type == "Admin":
            tk.Button(
                filter_bar,
                text="Delete Selected",
                command=self.delete_schedule,
                bg="#DC2626",
                fg="#FFFFFF",
                font=FONTS["small"],
                relief="flat",
                cursor="hand2",
                padx=8,
                pady=3
            ).pack(side="right")

        # Table
        table_frame = tk.Frame(self.tab_schedules, bg="#FFFFFF")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        cols = ("id", "event_name", "date", "time", "venue", "department", "status", "description")
        self.schedule_table = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.schedule_table.heading("id", text="ID")
        self.schedule_table.heading("event_name", text="Event Name")
        self.schedule_table.heading("date", text="Date")
        self.schedule_table.heading("time", text="Time")
        self.schedule_table.heading("venue", text="Venue")
        self.schedule_table.heading("department", text="Department")
        self.schedule_table.heading("status", text="Status")
        self.schedule_table.heading("description", text="Description")

        self.schedule_table.column("id", width=40, anchor="center")
        self.schedule_table.column("event_name", width=200, anchor="w")
        self.schedule_table.column("date", width=90, anchor="center")
        self.schedule_table.column("time", width=80, anchor="center")
        self.schedule_table.column("venue", width=160, anchor="w")
        self.schedule_table.column("department", width=90, anchor="center")
        self.schedule_table.column("status", width=80, anchor="center")
        self.schedule_table.column("description", width=220, anchor="w")

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.schedule_table.yview)
        self.schedule_table.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side="right", fill="y")
        self.schedule_table.pack(fill="both", expand=True)

        self.load_schedules()

    def load_schedules(self):
        for item in self.schedule_table.get_children():
            self.schedule_table.delete(item)

        q = self.search_entry.get().strip()
        dept = self.dept_filter_var.get()
        rows = get_schedules(query=q, department=dept)
        for r in rows:
            self.schedule_table.insert("", "end", values=(
                r["id"], r["event_name"], r["date"], r["time"],
                r["venue"], r["department"], r["status"], r["description"]
            ))

    def delete_schedule(self):
        sel = self.schedule_table.selection()
        if not sel:
            messagebox.showwarning("Notice", "Please select a schedule to delete.")
            return
        item = self.schedule_table.item(sel[0])["values"]
        sched_id = item[0]
        event_name = item[1]

        if messagebox.askyesno("Confirm", f"Delete schedule '{event_name}'?"):
            ok, msg = delete_schedule(sched_id)
            if ok:
                messagebox.showinfo("Success", "Schedule deleted.")
                self.load_schedules()
            else:
                messagebox.showerror("Error", msg)

    # ---------------------------------------------------------
    # TAB 2: ADD SCHEDULE (Admin & Committee)
    # ---------------------------------------------------------
    def build_add_schedule_tab(self):
        form_card = tk.Frame(self.tab_add_sched, bg="#F0F9FF", relief="solid", bd=1, padx=25, pady=20)
        form_card.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            form_card,
            text="Add New Event Schedule",
            font=FONTS["title"],
            fg="#0284C7",
            bg="#F0F9FF"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="w")

        # 1. Event Name
        tk.Label(form_card, text="Event Name *", font=FONTS["body_bold"], bg="#F0F9FF", fg="#0F172A").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_event_name = tk.Entry(form_card, font=FONTS["body"], bg="#FFFFFF", fg="#0F172A", relief="solid", bd=1, width=35)
        self.entry_event_name.grid(row=1, column=1, sticky="w", pady=5, padx=10, ipady=3)

        # 2. Date
        tk.Label(form_card, text="Date (YYYY-MM-DD) *", font=FONTS["body_bold"], bg="#F0F9FF", fg="#0F172A").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_date = tk.Entry(form_card, font=FONTS["body"], bg="#FFFFFF", fg="#0F172A", relief="solid", bd=1, width=35)
        self.entry_date.grid(row=2, column=1, sticky="w", pady=5, padx=10, ipady=3)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # 3. Time
        tk.Label(form_card, text="Time (e.g. 10:00 AM) *", font=FONTS["body_bold"], bg="#F0F9FF", fg="#0F172A").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_time = tk.Entry(form_card, font=FONTS["body"], bg="#FFFFFF", fg="#0F172A", relief="solid", bd=1, width=35)
        self.entry_time.grid(row=3, column=1, sticky="w", pady=5, padx=10, ipady=3)
        self.entry_time.insert(0, "10:00 AM")

        # 4. Venue
        tk.Label(form_card, text="Venue / Location *", font=FONTS["body_bold"], bg="#F0F9FF", fg="#0F172A").grid(row=4, column=0, sticky="w", pady=5)
        self.entry_venue = tk.Entry(form_card, font=FONTS["body"], bg="#FFFFFF", fg="#0F172A", relief="solid", bd=1, width=35)
        self.entry_venue.grid(row=4, column=1, sticky="w", pady=5, padx=10, ipady=3)

        # 5. Department
        tk.Label(form_card, text="Department *", font=FONTS["body_bold"], bg="#F0F9FF", fg="#0F172A").grid(row=5, column=0, sticky="w", pady=5)
        self.dept_add_var = tk.StringVar(value="College")
        dept_menu = ttk.Combobox(form_card, textvariable=self.dept_add_var, values=["College", "School", "Both"], state="readonly", width=33)
        dept_menu.grid(row=5, column=1, sticky="w", pady=5, padx=10)

        # 6. Description
        tk.Label(form_card, text="Description", font=FONTS["body_bold"], bg="#F0F9FF", fg="#0F172A").grid(row=6, column=0, sticky="nw", pady=5)
        self.entry_desc = tk.Text(form_card, height=3, width=35, font=FONTS["body"], bg="#FFFFFF", fg="#0F172A", relief="solid", bd=1)
        self.entry_desc.grid(row=6, column=1, sticky="w", pady=5, padx=10)

        # Buttons Row
        btn_box = tk.Frame(form_card, bg="#F0F9FF")
        btn_box.grid(row=7, column=1, sticky="w", pady=(15, 0), padx=10)

        # SAVE / ENTER BUTTON
        tk.Button(
            btn_box,
            text="Save Schedule / Enter",
            command=self.save_schedule,
            bg="#0284C7",
            fg="#FFFFFF",
            font=FONTS["body_bold"],
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            btn_box,
            text="Clear Form",
            command=self.clear_schedule_form,
            bg="#E2E8F0",
            fg="#0F172A",
            font=FONTS["body"],
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=6
        ).pack(side="left")

    def clear_schedule_form(self):
        self.entry_event_name.delete(0, tk.END)
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_time.delete(0, tk.END)
        self.entry_time.insert(0, "10:00 AM")
        self.entry_venue.delete(0, tk.END)
        self.entry_desc.delete("1.0", tk.END)

    def save_schedule(self):
        name = self.entry_event_name.get().strip()
        dt = self.entry_date.get().strip()
        tm = self.entry_time.get().strip()
        vn = self.entry_venue.get().strip()
        dept = self.dept_add_var.get()
        desc = self.entry_desc.get("1.0", tk.END).strip()

        if not (name and dt and tm and vn):
            messagebox.showerror("Error", "Please fill in Event Name, Date, Time, and Venue!")
            return

        ok, msg = add_schedule(name, dt, tm, vn, desc, department=dept, created_by=self.username)
        if ok:
            messagebox.showinfo("Success", "Schedule saved successfully!")
            self.clear_schedule_form()
            self.load_schedules()
            self.notebook.select(0)
        else:
            messagebox.showerror("Error", msg)

    # ---------------------------------------------------------
    # TAB 3: SHOWFLOW (ITINERARY)
    # ---------------------------------------------------------
    def build_showflow_tab(self):
        top_bar = tk.Frame(self.tab_showflow, bg="#F0F9FF", padx=10, pady=8, relief="solid", bd=1)
        top_bar.pack(fill="x", padx=10, pady=(10, 8))

        tk.Label(top_bar, text="Event Itinerary Flow", font=FONTS["body_bold"], bg="#F0F9FF", fg="#0F172A").pack(side="left")

        if self.user_type in ["Admin", "Committee"]:
            tk.Button(
                top_bar,
                text="➕ Add Activity",
                command=self.show_add_activity_dialog,
                bg="#0284C7",
                fg="#FFFFFF",
                font=FONTS["small"],
                relief="flat",
                cursor="hand2",
                padx=8,
                pady=3
            ).pack(side="right", padx=3)

            tk.Button(
                top_bar,
                text="Delete Activity",
                command=self.delete_activity,
                bg="#DC2626",
                fg="#FFFFFF",
                font=FONTS["small"],
                relief="flat",
                cursor="hand2",
                padx=8,
                pady=3
            ).pack(side="right", padx=3)

        table_frame = tk.Frame(self.tab_showflow, bg="#FFFFFF")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        cols = ("id", "event_name", "time_slot", "activity", "incharge", "remarks")
        self.showflow_table = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.showflow_table.heading("id", text="#")
        self.showflow_table.heading("event_name", text="Event Name")
        self.showflow_table.heading("time_slot", text="Time Slot")
        self.showflow_table.heading("activity", text="Activity / Agenda")
        self.showflow_table.heading("incharge", text="In-Charge")
        self.showflow_table.heading("remarks", text="Remarks")

        self.showflow_table.column("id", width=35, anchor="center")
        self.showflow_table.column("event_name", width=200, anchor="w")
        self.showflow_table.column("time_slot", width=140, anchor="center")
        self.showflow_table.column("activity", width=220, anchor="w")
        self.showflow_table.column("incharge", width=120, anchor="w")
        self.showflow_table.column("remarks", width=180, anchor="w")

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.showflow_table.yview)
        self.showflow_table.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side="right", fill="y")
        self.showflow_table.pack(fill="both", expand=True)

        self.load_showflow()

    def load_showflow(self):
        for item in self.showflow_table.get_children():
            self.showflow_table.delete(item)
        rows = get_showflow()
        for r in rows:
            self.showflow_table.insert("", "end", values=(
                r["id"], r["event_name"], r["time_slot"], r["activity"], r["incharge"], r["remarks"]
            ))

    def show_add_activity_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add Activity to Showflow")
        win.geometry("420x380")
        win.configure(bg="#F0F9FF")

        tk.Label(win, text="Add Showflow Activity", font=FONTS["title"], bg="#F0F9FF", fg="#0284C7").pack(pady=10)

        f = tk.Frame(win, bg="#F0F9FF", padx=15)
        f.pack(fill="x")

        tk.Label(f, text="Event Name *", font=FONTS["body_bold"], bg="#F0F9FF").pack(anchor="w")
        scheds = get_schedules()
        names = [s["event_name"] for s in scheds] if scheds else ["General Event"]
        ev_var = tk.StringVar(value=names[0])
        ev_cb = ttk.Combobox(f, textvariable=ev_var, values=names, state="readonly")
        ev_cb.pack(fill="x", pady=(2, 6))

        tk.Label(f, text="Time Slot (e.g. 10:00 AM - 10:30 AM) *", font=FONTS["body_bold"], bg="#F0F9FF").pack(anchor="w")
        ts_e = tk.Entry(f, font=FONTS["body"], relief="solid", bd=1)
        ts_e.pack(fill="x", pady=(2, 6), ipady=3)

        tk.Label(f, text="Activity Description *", font=FONTS["body_bold"], bg="#F0F9FF").pack(anchor="w")
        ac_e = tk.Entry(f, font=FONTS["body"], relief="solid", bd=1)
        ac_e.pack(fill="x", pady=(2, 6), ipady=3)

        tk.Label(f, text="In-Charge *", font=FONTS["body_bold"], bg="#F0F9FF").pack(anchor="w")
        ic_e = tk.Entry(f, font=FONTS["body"], relief="solid", bd=1)
        ic_e.pack(fill="x", pady=(2, 6), ipady=3)

        tk.Label(f, text="Remarks", font=FONTS["body_bold"], bg="#F0F9FF").pack(anchor="w")
        rm_e = tk.Entry(f, font=FONTS["body"], relief="solid", bd=1)
        rm_e.pack(fill="x", pady=(2, 10), ipady=3)

        def save_act():
            if not (ev_var.get() and ts_e.get() and ac_e.get() and ic_e.get()):
                messagebox.showerror("Error", "Please fill in all mandatory fields!")
                return
            ok, msg = add_showflow_item(ev_var.get(), ts_e.get(), ac_e.get(), ic_e.get(), rm_e.get())
            if ok:
                messagebox.showinfo("Success", "Activity added!")
                win.destroy()
                self.load_showflow()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(
            win,
            text="Save Activity / Enter",
            command=save_act,
            bg="#0284C7",
            fg="#FFFFFF",
            font=FONTS["body_bold"],
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6
        ).pack(pady=10)

    def delete_activity(self):
        sel = self.showflow_table.selection()
        if not sel:
            messagebox.showwarning("Notice", "Select an activity to delete.")
            return
        item_id = self.showflow_table.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirm", "Delete this activity?"):
            delete_showflow_item(item_id)
            self.load_showflow()

    # ---------------------------------------------------------
    # TAB 4: ENHANCED WORKSPACE NOTES
    # ---------------------------------------------------------
    def build_notes_tab(self):
        """Builds a beautiful 2-column workspace for notes with live update upon saving."""
        container = tk.Frame(self.tab_notes, bg="#FFFFFF", padx=12, pady=10)
        container.pack(fill="both", expand=True)

        # ----------------- LEFT PANE: SAVED NOTES LIST -----------------
        left_box = tk.Frame(container, bg="#F0F9FF", relief="solid", bd=1, width=340, padx=10, pady=10)
        left_box.pack(side="left", fill="y", padx=(0, 12))
        left_box.pack_propagate(False)

        # Left Header
        top_left_bar = tk.Frame(left_box, bg="#F0F9FF")
        top_left_bar.pack(fill="x", pady=(0, 8))

        tk.Label(
            top_left_bar,
            text="📝 Saved Notes",
            font=FONTS["subtitle"],
            bg="#F0F9FF",
            fg="#0F172A"
        ).pack(side="left")

        # New Note Button in Left Header
        tk.Button(
            top_left_bar,
            text="+ New Note",
            command=self.new_blank_note,
            bg="#0284C7",
            fg="#FFFFFF",
            font=FONTS["small"],
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=2
        ).pack(side="right")

        # Filter option (All Notes vs My Notes)
        filter_row = tk.Frame(left_box, bg="#F0F9FF")
        filter_row.pack(fill="x", pady=(0, 6))

        tk.Label(filter_row, text="Filter:", font=FONTS["small"], bg="#F0F9FF", fg="#475569").pack(side="left", padx=(0, 4))
        self.note_filter_var = tk.StringVar(value="All Notes")
        note_filter_cb = ttk.Combobox(filter_row, textvariable=self.note_filter_var, values=["All Notes", "My Notes"], state="readonly", width=12)
        note_filter_cb.pack(side="left")
        note_filter_cb.bind("<<ComboboxSelected>>", lambda e: self.load_notes())

        self.notes_count_lbl = tk.Label(filter_row, text="0 notes", font=FONTS["small"], bg="#F0F9FF", fg="#64748B")
        self.notes_count_lbl.pack(side="right")

        # Clean Table for Notes Directory
        list_frame = tk.Frame(left_box, bg="#FFFFFF", relief="solid", bd=1)
        list_frame.pack(fill="both", expand=True, pady=(0, 8))

        cols = ("id", "title", "author")
        self.notes_tree = ttk.Treeview(list_frame, columns=cols, show="headings", selectmode="browse")
        self.notes_tree.heading("id", text="#")
        self.notes_tree.heading("title", text="Title")
        self.notes_tree.heading("author", text="Author")

        self.notes_tree.column("id", width=30, anchor="center")
        self.notes_tree.column("title", width=180, anchor="w")
        self.notes_tree.column("author", width=75, anchor="center")

        tree_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.notes_tree.yview)
        self.notes_tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side="right", fill="y")
        self.notes_tree.pack(fill="both", expand=True)

        self.notes_tree.bind("<<TreeviewSelect>>", self.on_select_tree_note)

        # Left Bottom Action: Delete
        tk.Button(
            left_box,
            text="Delete Selected Note",
            command=self.delete_note_action,
            bg="#DC2626",
            fg="#FFFFFF",
            font=FONTS["small"],
            relief="flat",
            cursor="hand2",
            pady=4
        ).pack(fill="x")

        # ----------------- RIGHT PANE: NOTE EDITOR -----------------
        right_box = tk.Frame(container, bg="#F0F9FF", relief="solid", bd=1, padx=16, pady=14)
        right_box.pack(side="right", fill="both", expand=True)

        # Editor Header Banner
        editor_top = tk.Frame(right_box, bg="#F0F9FF")
        editor_top.pack(fill="x", pady=(0, 10))

        self.editor_mode_lbl = tk.Label(
            editor_top,
            text="➕ Creating New Note",
            font=FONTS["subtitle"],
            bg="#F0F9FF",
            fg="#0284C7"
        )
        self.editor_mode_lbl.pack(side="left")

        # Live feedback status
        self.note_status_lbl = tk.Label(
            editor_top,
            text="Ready to type",
            font=FONTS["small"],
            bg="#F0F9FF",
            fg="#64748B"
        )
        self.note_status_lbl.pack(side="right")

        # 1. Note Title Field
        tk.Label(right_box, text="Note Title *", font=FONTS["body_bold"], bg="#F0F9FF", fg="#0F172A").pack(anchor="w")
        self.note_title_entry = tk.Entry(
            right_box,
            font=("Segoe UI", 11, "bold"),
            bg="#FFFFFF",
            fg="#0F172A",
            relief="solid",
            bd=1
        )
        self.note_title_entry.pack(fill="x", pady=(3, 10), ipady=5)

        # 2. Note Content Field
        tk.Label(right_box, text="Note Content / Details *", font=FONTS["body_bold"], bg="#F0F9FF", fg="#0F172A").pack(anchor="w")
        
        text_frame = tk.Frame(right_box, bg="#FFFFFF", relief="solid", bd=1)
        text_frame.pack(fill="both", expand=True, pady=(3, 12))

        self.note_content_text = tk.Text(
            text_frame,
            font=FONTS["body"],
            bg="#FFFFFF",
            fg="#0F172A",
            relief="flat",
            bd=0,
            wrap="word",
            padx=8,
            pady=8
        )
        text_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.note_content_text.yview)
        self.note_content_text.configure(yscrollcommand=text_scroll.set)
        text_scroll.pack(side="right", fill="y")
        self.note_content_text.pack(fill="both", expand=True)

        # Real-time typing listeners for live auto-saving
        self.note_title_entry.bind("<KeyRelease>", self.on_note_typing)
        self.note_content_text.bind("<KeyRelease>", self.on_note_typing)

        # Enter key in Title entry moves focus to Note Content
        self.note_title_entry.bind("<Return>", lambda e: self.note_content_text.focus_set())

        # Ctrl+Return in Content immediately saves without popup
        self.note_content_text.bind("<Control-Return>", lambda e: self.save_note_action(silent=True))

        # 3. Action Buttons Row
        btn_row = tk.Frame(right_box, bg="#F0F9FF")
        btn_row.pack(fill="x")

        # SAVE NOTE BUTTON (Primary focus)
        self.btn_save_note = tk.Button(
            btn_row,
            text="💾 Save Note / Enter",
            command=self.save_note_action,
            bg="#0284C7",
            fg="#FFFFFF",
            activebackground="#0369A1",
            activeforeground="#FFFFFF",
            font=FONTS["body_bold"],
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=7
        )
        self.btn_save_note.pack(side="right", padx=(8, 0))

        # Clear / New Blank Note Button
        tk.Button(
            btn_row,
            text="Clear / New",
            command=self.new_blank_note,
            bg="#E2E8F0",
            fg="#0F172A",
            font=FONTS["body"],
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=7
        ).pack(side="right")

        # Keyboard Shortcut Ctrl+S to save
        self.root.bind("<Control-s>", lambda e: self.save_note_action(silent=True))

        # Load notes initially
        self.load_notes()

    def load_notes(self):
        """Reloads notes from database and immediately reflects in the notes table."""
        for item in self.notes_tree.get_children():
            self.notes_tree.delete(item)

        filter_choice = self.note_filter_var.get()
        user_filter = self.username if filter_choice == "My Notes" else None

        self.notes_data = get_notes(user_filter)
        self.notes_count_lbl.config(text=f"{len(self.notes_data)} notes")

        for n in self.notes_data:
            self.notes_tree.insert("", "end", values=(
                n["id"],
                n["title"],
                n["username"]
            ))

    def on_select_tree_note(self, event=None):
        """When a note is clicked in the list, flush any pending save and load the note."""
        if self._is_auto_saving:
            return

        sel = self.notes_tree.selection()
        if not sel:
            return
        item_vals = self.notes_tree.item(sel[0])["values"]
        if not item_vals:
            return
        note_id = item_vals[0]

        # If this note is already active in the editor, do not reload or overwrite status
        if self.current_selected_note_id is not None and str(note_id) == str(self.current_selected_note_id):
            return

        # Flush any pending auto-save for current note before switching to a different note
        if self._auto_save_timer is not None:
            self.auto_save_note()

        for n in self.notes_data:
            if str(n["id"]) == str(note_id):
                self.current_selected_note_id = n["id"]
                self.note_title_entry.delete(0, tk.END)
                self.note_title_entry.insert(0, n["title"])
                self.note_content_text.delete("1.0", tk.END)
                self.note_content_text.insert("1.0", n["content"])

                self.editor_mode_lbl.config(text=f"✏️ Editing Note #{n['id']}")
                self.note_status_lbl.config(text=f"Author: {n['username']}", fg="#0369A1")
                break

    def on_note_typing(self, event=None):
        """Debounces user keystrokes and auto-saves 600ms after user pauses typing."""
        self.note_status_lbl.config(text="Typing...", fg="#D97706")
        if self._auto_save_timer is not None:
            self.root.after_cancel(self._auto_save_timer)
        self._auto_save_timer = self.root.after(600, self.auto_save_note)

    def auto_save_note(self):
        """Automatically saves typed content to SQLite and updates the notes list in real time."""
        if self._auto_save_timer is not None:
            try:
                self.root.after_cancel(self._auto_save_timer)
            except Exception:
                pass
            self._auto_save_timer = None

        title = self.note_title_entry.get().strip()
        content = self.note_content_text.get("1.0", tk.END).strip()

        # Do not save if both title and content are empty
        if not title and not content:
            return

        # If title is empty but content is being typed, use first line of content as title
        if not title and content:
            first_line = content.split("\n")[0][:25].strip()
            title = first_line if first_line else "Untitled Note"

        target_id = self.current_selected_note_id
        self._is_auto_saving = True
        try:
            if target_id is not None:
                # Update existing note in DB and update tree view row in place
                ok, _ = update_note(target_id, title, content)
                if ok:
                    for child in self.notes_tree.get_children():
                        vals = self.notes_tree.item(child)["values"]
                        if vals and str(vals[0]) == str(target_id):
                            author = vals[2] if len(vals) > 2 else self.username
                            self.notes_tree.item(child, values=(target_id, title, author))
                            break
                    for n in self.notes_data:
                        if n["id"] == target_id:
                            n["title"] = title
                            n["content"] = content
                            break
                    now_str = datetime.now().strftime("%I:%M:%S %p")
                    self.note_status_lbl.config(text=f"✔ Auto-saved at {now_str}", fg="#16A34A")
            elif title:
                # Create new note in DB and highlight it in the list
                ok, _ = add_note(self.username, title, content)
                if ok:
                    self.load_notes()
                    if self.notes_data:
                        latest_id = self.notes_data[0]["id"]
                        self.current_selected_note_id = latest_id
                        self.select_note_in_tree(latest_id)
                    now_str = datetime.now().strftime("%I:%M:%S %p")
                    self.note_status_lbl.config(text=f"✔ Auto-saved at {now_str}", fg="#16A34A")
                    self.editor_mode_lbl.config(text=f"✏️ Editing Note #{self.current_selected_note_id}")
        finally:
            self._is_auto_saving = False

    def new_blank_note(self):
        """Clears the editor so the user can type and save a fresh note."""
        if self._auto_save_timer is not None:
            try:
                self.root.after_cancel(self._auto_save_timer)
            except Exception:
                pass
            self._auto_save_timer = None

        self.current_selected_note_id = None
        self.note_title_entry.delete(0, tk.END)
        self.note_content_text.delete("1.0", tk.END)
        self.editor_mode_lbl.config(text="➕ Creating New Note")
        self.note_status_lbl.config(text="New Draft", fg="#64748B")
        self.notes_tree.selection_remove(self.notes_tree.selection())
        self.note_title_entry.focus_set()

    def select_note_in_tree(self, target_id):
        """Finds and highlights a note in the Treeview by ID."""
        for child in self.notes_tree.get_children():
            vals = self.notes_tree.item(child)["values"]
            if vals and str(vals[0]) == str(target_id):
                self.notes_tree.selection_set(child)
                self.notes_tree.focus(child)
                self.notes_tree.see(child)
                break

    def save_note_action(self, silent=False):
        """
        Saves the note into SQLite.
        Immediately reflects the saved note in the notes directory list and selects it!
        """
        if self._auto_save_timer is not None:
            try:
                self.root.after_cancel(self._auto_save_timer)
            except Exception:
                pass
            self._auto_save_timer = None

        title = self.note_title_entry.get().strip()
        content = self.note_content_text.get("1.0", tk.END).strip()

        if not title:
            if not silent:
                messagebox.showerror("Error", "Please enter a Title for the note!")
                self.note_title_entry.focus_set()
            return

        if not content:
            if not silent:
                messagebox.showerror("Error", "Please enter Content for the note!")
                self.note_content_text.focus_set()
            return

        target_id = self.current_selected_note_id

        if target_id is not None:
            # Updating an existing note
            ok, msg = update_note(target_id, title, content)
        else:
            # Adding a brand new note
            ok, msg = add_note(self.username, title, content)

        if ok:
            # 1. Immediately reload notes so the list reflects the new/updated note
            self.load_notes()

            # 2. Re-select the saved note in the list
            if target_id is not None:
                self.select_note_in_tree(target_id)
            elif self.notes_data:
                # The newest note is at the top of the list
                latest_id = self.notes_data[0]["id"]
                self.current_selected_note_id = latest_id
                self.select_note_in_tree(latest_id)

            now_str = datetime.now().strftime("%I:%M:%S %p")
            self.note_status_lbl.config(text=f"✔ Saved at {now_str}", fg="#16A34A")
            self.editor_mode_lbl.config(text=f"✏️ Editing Note: {title[:20]}")

            if not silent:
                messagebox.showinfo("Success", "Note saved and reflected in your notes list!")
        else:
            if not silent:
                messagebox.showerror("Error", msg)

    def delete_note_action(self):
        """Deletes the selected note and clears the editor."""
        if self._auto_save_timer is not None:
            try:
                self.root.after_cancel(self._auto_save_timer)
            except Exception:
                pass
            self._auto_save_timer = None

        sel = self.notes_tree.selection()
        if not sel:
            messagebox.showwarning("Notice", "Please select a note from the list to delete.")
            return

        note_id = self.notes_tree.item(sel[0])["values"][0]
        note_title = self.notes_tree.item(sel[0])["values"][1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete note:\n'{note_title}'?"):
            ok, msg = delete_note(note_id)
            if ok:
                self.new_blank_note()
                self.load_notes()
                messagebox.showinfo("Deleted", "Note removed successfully.")
            else:
                messagebox.showerror("Error", msg)

    # ---------------------------------------------------------
    # STATUS BAR & ACTIONS
    # ---------------------------------------------------------
    def build_statusbar(self):
        bar = tk.Frame(self.canvas, bg="#E0F2FE", height=24, padx=12)
        bar.pack(fill="x", side="bottom")

        tk.Label(bar, text="Status: Connected (SQLite) | S C H E D Z System Ready", bg="#E0F2FE", fg="#0369A1", font=FONTS["small"]).pack(side="left")
        tk.Label(bar, text=f"Logged in: {self.username} ({self.user_type})", bg="#E0F2FE", fg="#0369A1", font=FONTS["small"]).pack(side="right")

    def export_csv(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], initialfile="schedz_export.csv")
        if not filepath:
            return
        rows = get_schedules()
        try:
            with open(filepath, mode="w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["ID", "Event Name", "Date", "Time", "Venue", "Department", "Status", "Description"])
                for r in rows:
                    w.writerow([r["id"], r["event_name"], r["date"], r["time"], r["venue"], r["department"], r["status"], r["description"]])
            messagebox.showinfo("Success", f"Schedules exported to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    def logout(self):
        if messagebox.askyesno("Sign Out", "Are you sure you want to sign out?"):
            self.root.destroy()
            login_script = os.path.join(os.path.dirname(__file__), "SCHEDZ_LOGIN.py")
            subprocess.run([sys.executable, login_script])


def main():
    user_type = sys.argv[1] if len(sys.argv) > 1 else "Admin"
    username = sys.argv[2] if len(sys.argv) > 2 else "admin"

    root = tk.Tk()
    app = SchedzHomepage(root, user_type=user_type, username=username)
    root.mainloop()


if __name__ == "__main__":
    main()
