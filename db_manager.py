"""
SCHEDZ - Database Management Module
Uses Python's built-in sqlite3 for zero-configuration, reliable local persistence.
Provides automatic schema setup, seeding, and secure authentication.
"""

import sqlite3
import hashlib
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schedz.db")


def hash_password(password: str) -> str:
    """Hash password using SHA-256 for basic open-source project security."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_connection():
    """Returns a sqlite3 connection with row dictionary access."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables and seeds initial mock data if database is fresh."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users Table (matching USER_MAGMT schema)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS USER_MAGMT (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT UNIQUE NOT NULL,
            Email TEXT NOT NULL,
            PhoneNo TEXT,
            Passwrd TEXT NOT NULL,
            User_type TEXT NOT NULL,
            DEPARTMENT TEXT NOT NULL,
            Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Schedules Table (matching SCHEDULE schema)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SCHEDULE (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            venue TEXT NOT NULL,
            description TEXT,
            department TEXT DEFAULT 'College',
            status TEXT DEFAULT 'Scheduled',
            created_by TEXT DEFAULT 'Admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Notes Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS NOTES (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 4. Showflow Table (Timeline breakdown of event activities)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SHOWFLOW (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            event_name TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            activity TEXT NOT NULL,
            incharge TEXT NOT NULL,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # Seed initial test data if empty
    cursor.execute("SELECT COUNT(*) FROM USER_MAGMT")
    user_count = cursor.fetchone()[0]

    if user_count == 0:
        seed_users = [
            ("admin", "admin@schedz.org", "+91 9876543210", hash_password("admin123"), "Admin", "College"),
            ("committee", "committee@schedz.org", "+91 9876543211", hash_password("comm123"), "Committee", "College"),
            ("student", "student@schedz.org", "+91 9876543212", hash_password("stud123"), "Student", "College"),
            ("principal", "lead@school.org", "+91 9876543213", hash_password("school123"), "Admin", "School"),
        ]
        cursor.executemany("""
            INSERT INTO USER_MAGMT (Username, Email, PhoneNo, Passwrd, User_type, DEPARTMENT)
            VALUES (?, ?, ?, ?, ?, ?)
        """, seed_users)

    cursor.execute("SELECT COUNT(*) FROM SCHEDULE")
    schedule_count = cursor.fetchone()[0]

    if schedule_count == 0:
        seed_schedules = [
            (
                "Open Source Lab Project Showcase",
                "2026-10-09",
                "10:00 AM",
                "Lab 302, Computing Block",
                "Presentation and evaluation of final open source projects with live demonstrations.",
                "College",
                "Upcoming",
                "admin"
            ),
            (
                "Annual Tech Symposium 2026",
                "2026-10-15",
                "09:30 AM",
                "Main Auditorium",
                "Keynote address by industry experts, hackathon kickoff, and student project exhibitions.",
                "College",
                "Scheduled",
                "committee"
            ),
            (
                "AI & Robotics Hands-on Workshop",
                "2026-10-22",
                "02:00 PM",
                "Seminar Hall B",
                "Interactive session on agentic workflows, machine learning architectures, and robotics control.",
                "College",
                "Scheduled",
                "admin"
            ),
            (
                "Inter-School Science & Coding Carnival",
                "2026-11-05",
                "09:00 AM",
                "Campus Sports Complex",
                "Exhibits, robotics battles, and speed programming challenges for high school participants.",
                "School",
                "Planning",
                "principal"
            ),
        ]
        cursor.executemany("""
            INSERT INTO SCHEDULE (event_name, date, time, venue, description, department, status, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_schedules)

    cursor.execute("SELECT COUNT(*) FROM NOTES")
    note_count = cursor.fetchone()[0]

    if note_count == 0:
        seed_notes = [
            ("admin", "Evaluation Criteria Checklist", "Ensure repository README, modular structure, database persistence, and role-based views are demonstrated."),
            ("committee", "Auditorium Setup Checklist", "Check projector cables, wireless microphones, podium arrangement, and registration badges."),
            ("student", "Project Demo Prep", "Review Tkinter event loop handling, SQLite query optimization, and test all user roles prior to review."),
        ]
        cursor.executemany("""
            INSERT INTO NOTES (username, title, content)
            VALUES (?, ?, ?)
        """, seed_notes)

    cursor.execute("SELECT COUNT(*) FROM SHOWFLOW")
    showflow_count = cursor.fetchone()[0]

    if showflow_count == 0:
        seed_showflow = [
            (1, "Open Source Lab Project Showcase", "10:00 AM - 10:15 AM", "Welcome Address & Lab Briefing", "Prof. Guide", "All batches assemble"),
            (1, "Open Source Lab Project Showcase", "10:15 AM - 11:30 AM", "Batch 1: Software Architecture Demos", "Evaluator Panel", "10 mins per project team"),
            (1, "Open Source Lab Project Showcase", "11:30 AM - 11:45 AM", "Tea & Networking Break", "Committee", "Cafeteria area"),
            (1, "Open Source Lab Project Showcase", "11:45 AM - 01:00 PM", "Batch 2: Advanced System Projects", "Evaluator Panel", "Q&A and Code Reviews"),
            (2, "Annual Tech Symposium 2026", "09:30 AM - 10:00 AM", "Registration & Delegate Welcome", "Student Volunteers", "Kit distribution"),
            (2, "Annual Tech Symposium 2026", "10:00 AM - 11:00 AM", "Keynote: Future of Open Source", "Chief Guest", "Main Stage"),
        ]
        cursor.executemany("""
            INSERT INTO SHOWFLOW (event_id, event_name, time_slot, activity, incharge, remarks)
            VALUES (?, ?, ?, ?, ?, ?)
        """, seed_showflow)

    conn.commit()
    conn.close()


# User Authentication & Management
def authenticate_user(username, password):
    """Verifies username and password, returns (success: bool, user_info: dict, message: str)."""
    if not username or not password:
        return False, None, "Please enter both username and password."

    conn = get_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)

    # Check both hashed and plain text (for backward compatibility if plain password was entered previously)
    cursor.execute("""
        SELECT * FROM USER_MAGMT 
        WHERE LOWER(Username) = LOWER(?) AND (Passwrd = ? OR Passwrd = ?)
    """, (username.strip(), pwd_hash, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return True, dict(user), f"Welcome {user['Username']}!"
    return False, None, "Invalid username or password."


def register_user(username, email, phone, password, user_type, department):
    """Registers a new user into USER_MAGMT with validation."""
    # 1. All fields required
    if not (username and email and phone and password and user_type and department):
        return False, "All fields are required! Please fill in all fields before submitting."

    username = username.strip()
    email = email.strip()
    phone = phone.strip()

    # 2. Maximum 20 characters for name
    if len(username) > 20:
        return False, f"Username/Name cannot exceed 20 characters (current length: {len(username)})."

    # 3. Exactly 10 digits in phone number
    if not (phone.isdigit() and len(phone) == 10):
        return False, "Phone number must contain exactly 10 digits."

    # 4. Email must contain @gmail.com
    email_lower = email.lower()
    if not (email_lower.endswith("@gmail.com") and len(email_lower) > len("@gmail.com")):
        return False, "Email must be a valid address ending with @gmail.com."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if username exists
        cursor.execute("SELECT id FROM USER_MAGMT WHERE LOWER(Username) = LOWER(?)", (username,))
        if cursor.fetchone():
            conn.close()
            return False, f"Username '{username}' is already taken. Please choose another."

        pwd_hash = hash_password(password)
        cursor.execute("""
            INSERT INTO USER_MAGMT (Username, Email, PhoneNo, Passwrd, User_type, DEPARTMENT)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, email, phone, pwd_hash, user_type, department))
        conn.commit()
        conn.close()
        return True, "User registered successfully!"
    except sqlite3.IntegrityError as e:
        conn.close()
        return False, f"Registration failed: {e}"
    except Exception as e:
        conn.close()
        return False, f"Database error: {e}"


# Schedule Management
def get_schedules(query=None, department=None, order_by="id ASC"):
    """Retrieves schedules in increasing numeric order by ID with optional search query and department filter."""
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT * FROM SCHEDULE WHERE 1=1"
    params = []

    if query:
        sql += " AND (event_name LIKE ? OR venue LIKE ? OR description LIKE ?)"
        q = f"%{query}%"
        params.extend([q, q, q])

    if department and department != "All":
        sql += " AND (department = ? OR department = 'Both')"
        params.append(department)

    sql += f" ORDER BY {order_by}"

    cursor.execute(sql, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def add_schedule(event_name, date, time, venue, description, department="College", status="Upcoming", created_by="Admin"):
    """Adds a new schedule with an iterated numeric ID in increasing order."""
    if not all([event_name, date, time, venue]):
        return False, "Event name, Date, Time, and Venue are required."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*) FROM SCHEDULE
            WHERE LOWER(event_name) = LOWER(?) AND date = ? AND time = ?
        """, (event_name.strip(), date.strip(), time.strip()))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "A schedule with the same event name, date, and time already exists!"

        # Ensure next ID iterates sequentially in increasing numeric order
        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM SCHEDULE")
        next_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO SCHEDULE (id, event_name, date, time, venue, description, department, status, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (next_id, event_name.strip(), date.strip(), time.strip(), venue.strip(), description.strip(), department, status, created_by))
        cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'SCHEDULE'", (next_id,))
        conn.commit()
        conn.close()
        return True, "Schedule added successfully!"
    except Exception as e:
        conn.close()
        return False, f"Failed to add schedule: {e}"


def delete_schedule(schedule_id):
    """Deletes a schedule by its ID and synchronizes sequence counter."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM SCHEDULE WHERE id = ?", (schedule_id,))
        cursor.execute("DELETE FROM SHOWFLOW WHERE event_id = ?", (schedule_id,))
        cursor.execute("SELECT COALESCE(MAX(id), 0) FROM SCHEDULE")
        max_id = cursor.fetchone()[0]
        cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'SCHEDULE'", (max_id,))
        conn.commit()
        conn.close()
        return True, "Schedule removed successfully."
    except Exception as e:
        conn.close()
        return False, f"Error deleting schedule: {e}"


# Notes Management
def get_notes(username=None):
    """Retrieves notes. If username is given, retrieves notes for that user or all notes if Admin."""
    conn = get_connection()
    cursor = conn.cursor()
    if username:
        cursor.execute("SELECT * FROM NOTES WHERE username = ? ORDER BY id DESC", (username,))
    else:
        cursor.execute("SELECT * FROM NOTES ORDER BY id DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def add_note(username, title, content):
    """Adds a new note."""
    if not title or not content:
        return False, "Title and content cannot be empty."
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO NOTES (username, title, content) VALUES (?, ?, ?)",
                       (username, title.strip(), content.strip()))
        conn.commit()
        conn.close()
        return True, "Note saved successfully!"
    except Exception as e:
        conn.close()
        return False, f"Failed to save note: {e}"


def update_note(note_id, title, content):
    """Updates an existing note by ID."""
    if not title or not content:
        return False, "Title and content cannot be empty."
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE NOTES SET title = ?, content = ? WHERE id = ?",
                       (title.strip(), content.strip(), note_id))
        conn.commit()
        conn.close()
        return True, "Note updated successfully!"
    except Exception as e:
        conn.close()
        return False, f"Failed to update note: {e}"


def delete_note(note_id):
    """Deletes a note."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM NOTES WHERE id = ?", (note_id,))
        conn.commit()
        conn.close()
        return True, "Note deleted."
    except Exception as e:
        conn.close()
        return False, str(e)


# Showflow Management
def get_showflow(event_name=None):
    """Retrieves showflow timeline items."""
    conn = get_connection()
    cursor = conn.cursor()
    if event_name and event_name != "All Events":
        cursor.execute("SELECT * FROM SHOWFLOW WHERE event_name = ? ORDER BY id ASC", (event_name,))
    else:
        cursor.execute("SELECT * FROM SHOWFLOW ORDER BY event_name ASC, id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def add_showflow_item(event_name, time_slot, activity, incharge, remarks=""):
    """Adds a new timeline activity to the event showflow."""
    if not all([event_name, time_slot, activity, incharge]):
        return False, "Event, Time Slot, Activity, and Incharge are required."
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO SHOWFLOW (event_name, time_slot, activity, incharge, remarks)
            VALUES (?, ?, ?, ?, ?)
        """, (event_name.strip(), time_slot.strip(), activity.strip(), incharge.strip(), remarks.strip()))
        conn.commit()
        conn.close()
        return True, "Showflow activity added successfully!"
    except Exception as e:
        conn.close()
        return False, str(e)


def delete_showflow_item(item_id):
    """Deletes a showflow activity item."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM SHOWFLOW WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        return True, "Activity deleted."
    except Exception as e:
        conn.close()
        return False, str(e)


# Statistics
def get_dashboard_stats():
    """Returns quick metrics for the dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM SCHEDULE")
    total_events = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM USER_MAGMT")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM NOTES")
    total_notes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM SHOWFLOW")
    total_activities = cursor.fetchone()[0]

    conn.close()
    return {
        "events": total_events,
        "users": total_users,
        "notes": total_notes,
        "activities": total_activities
    }


# Auto-initialize when imported
init_db()

if __name__ == "__main__":
    print(f"Database initialized at: {DB_FILE}")
    print("Stats:", get_dashboard_stats())
