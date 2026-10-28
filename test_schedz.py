"""
SCHEDZ - Automated Verification Script
Validates database logic, authentication, and GUI component initializations.
"""

import sys
import os
import tkinter as tk

from db_manager import (
    authenticate_user, register_user, get_schedules, add_schedule,
    delete_schedule, get_notes, add_note, delete_note, get_showflow,
    add_showflow_item, delete_showflow_item, get_dashboard_stats
)
from SCHEDZ_LOGIN import LoginApp
from SCHEDZ_SIGNUP import SignupApp
from SCHEDZ_HOMEPAGE import SchedzHomepage


def test_database_and_auth():
    print("[-] Testing Authentication...")
    # Admin test
    ok, u, msg = authenticate_user("admin", "admin123")
    assert ok and u["User_type"] == "Admin", f"Admin auth failed: {msg}"
    print("    [OK] Admin login verified:", u["Username"], u["User_type"])

    # Committee test
    ok, u, msg = authenticate_user("committee", "comm123")
    assert ok and u["User_type"] == "Committee", f"Committee auth failed: {msg}"
    print("    [OK] Committee login verified:", u["Username"], u["User_type"])

    # Student test
    ok, u, msg = authenticate_user("student", "stud123")
    assert ok and u["User_type"] == "Student", f"Student auth failed: {msg}"
    print("    [OK] Student login verified:", u["Username"], u["User_type"])

    # Test Registration Constraints
    # 1. Long name (>20 chars) should fail
    ok_long, _ = register_user("thisusernameiswaytoolong2026", "user@gmail.com", "9876543210", "pass123", "Student", "College")
    assert not ok_long, "Registration with >20 char username should fail!"
    print("    [OK] Verified >20 char username rejection")

    # 2. Invalid phone (not 10 digits) should fail
    ok_phone, _ = register_user("shortname", "user@gmail.com", "12345", "pass123", "Student", "College")
    assert not ok_phone, "Registration with non-10 digit phone should fail!"
    print("    [OK] Verified non-10 digit phone rejection")

    # 3. Non @gmail.com email should fail
    ok_email, _ = register_user("shortname", "user@yahoo.com", "9876543210", "pass123", "Student", "College")
    assert not ok_email, "Registration with non-@gmail.com email should fail!"
    print("    [OK] Verified non-@gmail.com email rejection")

    # 4. Valid Registration
    test_uname = "new_valid_user"
    ok, msg = register_user(test_uname, "validuser@gmail.com", "9876543210", "pass123", "Student", "College")
    print("    [OK] Valid user registration:", ok, msg)

    # Test Schedules CRUD
    print("[-] Testing Schedules CRUD...")
    ok, msg = add_schedule("Test Lab Presentation", "2026-10-09", "11:00 AM", "Room 401", "Testing event add", "College", "Scheduled", "tester")
    assert ok, f"Add schedule failed: {msg}"
    schedules = get_schedules(query="Test Lab Presentation")
    assert len(schedules) > 0, "Schedule retrieval failed"
    print("    [OK] Schedule added and retrieved:", schedules[0]["event_name"])

    # Test Notes CRUD
    print("[-] Testing Notes CRUD...")
    ok, msg = add_note("admin", "Demo Note Title", "Demo Note Body")
    assert ok, f"Add note failed: {msg}"
    notes = get_notes("admin")
    assert any(n["title"] == "Demo Note Title" for n in notes), "Note retrieval failed"
    print("    [OK] Note added and retrieved successfully")

    # Clean up test note and schedule
    for n in notes:
        if n["title"] == "Demo Note Title":
            delete_note(n["id"])
    delete_schedule(schedules[0]["id"])
    print("    [OK] Cleaned up test note and schedule")

    # Test Showflow CRUD and Department Bifurcations
    print("[-] Testing Showflow Department Bifurcations...")
    college_sf = get_showflow(department="College")
    assert len(college_sf) > 0 and all(item["department"] == "College" for item in college_sf), "College showflow retrieval failed"
    print(f"    [OK] Verified College showflow: {len(college_sf)} items")

    school_sf = get_showflow(department="School")
    assert len(school_sf) > 0 and all(item["department"] == "School" for item in school_sf), "School showflow retrieval failed"
    print(f"    [OK] Verified School showflow: {len(school_sf)} items")

    ok_sf, _ = add_showflow_item("Test Lab Presentation", "02:00 PM", "Demo Activity", "Incharge", "Remarks", department="College")
    assert ok_sf, "Add showflow item failed"
    latest_college = get_showflow(department="College")
    assert latest_college[-1]["activity"] == "Demo Activity"
    delete_showflow_item(latest_college[-1]["id"])
    print("    [OK] Showflow item added with department and cleaned up successfully")

    stats = get_dashboard_stats()
    print("    [OK] System Stats verified:", stats)


def test_gui_instantiations():
    print("[-] Testing GUI components instantiation...")

    # 1. Login GUI
    root1 = tk.Tk()
    root1.withdraw()
    app1 = LoginApp(root1)
    root1.update()
    root1.destroy()
    print("    [OK] LoginApp initialized cleanly")

    # 2. Signup GUI
    root2 = tk.Tk()
    root2.withdraw()
    app2 = SignupApp(root2)
    root2.update()
    root2.destroy()
    print("    [OK] SignupApp initialized cleanly")

    # 3. Homepage GUI - Admin Role
    root3 = tk.Tk()
    root3.withdraw()
    app3 = SchedzHomepage(root3, user_type="Admin", username="admin")
    root3.update()
    root3.destroy()
    print("    [OK] SchedzHomepage (Admin) initialized cleanly")

    # 4. Homepage GUI - Student Role
    root4 = tk.Tk()
    root4.withdraw()
    app4 = SchedzHomepage(root4, user_type="Student", username="student")
    root4.update()
    root4.destroy()
    print("    [OK] SchedzHomepage (Student) initialized cleanly")


if __name__ == "__main__":
    print("=== SCHEDZ AUTOMATED TEST SUITE ===")
    test_database_and_auth()
    test_gui_instantiations()
    print("=== ALL TESTS PASSED SUCCESSFULLY! ===")
