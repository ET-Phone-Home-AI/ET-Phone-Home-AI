# save this as attendance_system.py
# ------------------------------------------------------------
# AI Class Attendance System
#
# Works with any USB RFID reader that acts as a keyboard (it
# "types" the tag's ID and hits Enter when a card is scanned) --
# or just type an ID by hand to test without any hardware at all.
#
# Install: nothing extra needed! Only uses Python's built-in
# sqlite3 module.
#
# Run it with:  python attendance_system.py
# ------------------------------------------------------------

import sqlite3
import sys
from datetime import datetime, date

DB_FILE = "attendance.db"


def get_connection():
    # Connect to (or create) the database file on disk
    return sqlite3.connect(DB_FILE)


def init_db():
    # Create the tables the first time the program runs.
    # IF NOT EXISTS means this is safe to call every time.
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            tag_uid TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT,
            fun_fact TEXT,
            added_on TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_uid TEXT NOT NULL,
            session_date TEXT NOT NULL,
            scanned_at TEXT NOT NULL,
            UNIQUE(tag_uid, session_date)
        )
    """)
    conn.commit()
    conn.close()


def scan_tag_input(prompt="Scan a tag (or type its ID) > "):
    # Reads one line from the keyboard / RFID reader. A keyboard-wedge
    # RFID reader just "types" the tag ID and presses Enter, so a plain
    # input() call catches it exactly the same as manual typing.
    return input(prompt).strip()


def add_entry():
    print("\n--- Add New Entry ---")
    uid = scan_tag_input("Scan the new tag (or type an ID) > ")
    if not uid:
        print("No tag ID entered. Cancelled.\n")
        return

    conn = get_connection()
    existing = conn.execute(
        "SELECT name FROM students WHERE tag_uid = ?", (uid,)
    ).fetchone()
    if existing:
        print(f"That tag is already registered to {existing[0]}.\n")
        conn.close()
        return

    name = input("Student name : ").strip()
    department = input("Department  : ").strip()
    fun_fact = input("Fun Fact    : ").strip()
    added_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn.execute(
        "INSERT INTO students (tag_uid, name, department, fun_fact, added_on) "
        "VALUES (?, ?, ?, ?, ?)",
        (uid, name, department, fun_fact, added_on),
    )
    conn.commit()
    conn.close()
    print(f"Saved! {name} is now registered.\n")


def show_database():
    print("\n--- Show Database ---")
    conn = get_connection()
    rows = conn.execute(
        "SELECT name FROM students ORDER BY name ASC"
    ).fetchall()
    conn.close()

    if not rows:
        print("No students registered yet.\n")
        return

    print()
    for (name,) in rows:
        print(f"  {name}")
    print()


def print_tag_card(row):
    # row = (tag_uid, name, department, fun_fact, added_on)
    _, name, department, fun_fact, added_on = row
    fields = [
        ("Name", name),
        ("Department", department),
        ("Fun Fact", fun_fact),
        ("Added on", added_on),
    ]
    label_width = max(len(label) for label, _ in fields)
    inner_width = max(
        max(label_width + 3 + len(value) for label, value in fields),
        len("TAG RECOGNIZED") + 2,
    )

    top = "╔" + "═" * (inner_width + 2) + "╗"
    sep = "╠" + "═" * (inner_width + 2) + "╣"
    bot = "╚" + "═" * (inner_width + 2) + "╝"

    print(top)
    print(f"║ ✓ {'TAG RECOGNIZED'.ljust(inner_width - 2)} ║")
    print(sep)
    for label, value in fields:
        text = f"{label.ljust(label_width)} : {value}"
        print(f"║ {text.ljust(inner_width)} ║")
    print(bot)


def scan_tag():
    print("\n--- Scan a Tag ---")
    uid = scan_tag_input()
    if not uid:
        print("No tag scanned.\n")
        return

    conn = get_connection()
    row = conn.execute(
        "SELECT tag_uid, name, department, fun_fact, added_on "
        "FROM students WHERE tag_uid = ?",
        (uid,),
    ).fetchone()
    conn.close()

    if row:
        print()
        print_tag_card(row)
        print()
    else:
        print("Tag not recognized. Add it first with option 1.\n")


def take_attendance():
    print("\n--- Take Attendance ---")
    print("Scan tags one at a time. Press Enter on a blank line to stop.\n")
    today = date.today().isoformat()
    conn = get_connection()

    while True:
        uid = scan_tag_input()
        if not uid:
            break

        student = conn.execute(
            "SELECT name FROM students WHERE tag_uid = ?", (uid,)
        ).fetchone()
        if not student:
            print("  -> Unknown tag. Not recorded.\n")
            continue

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn.execute(
                "INSERT INTO attendance (tag_uid, session_date, scanned_at) "
                "VALUES (?, ?, ?)",
                (uid, today, now),
            )
            conn.commit()
            print(f"  -> Present: {student[0]}\n")
        except sqlite3.IntegrityError:
            print(f"  -> {student[0]} was already marked present today.\n")

    conn.close()
    print("Attendance session ended.\n")


def attendance_list():
    print("\n--- Attendance List ---")
    conn = get_connection()
    rows = conn.execute(
        "SELECT a.session_date, s.name, s.department, a.scanned_at "
        "FROM attendance a JOIN students s ON a.tag_uid = s.tag_uid "
        "ORDER BY a.session_date DESC, a.scanned_at ASC"
    ).fetchall()
    conn.close()

    if not rows:
        print("No attendance recorded yet.\n")
        return

    current_date = None
    for session_date, name, department, scanned_at in rows:
        if session_date != current_date:
            current_date = session_date
            print(f"\nDate: {current_date}")
            print("-" * 40)
        time_only = scanned_at.split(" ")[1]
        print(f"  {time_only}  {name} ({department})")
    print()


def delete_database():
    print("\n--- Delete the Database ---")
    confirm = input(
        "This will permanently delete ALL students and attendance "
        "records. Continue? (Y/N) > "
    ).strip().upper()
    if confirm == "Y":
        conn = get_connection()
        conn.execute("DROP TABLE IF EXISTS attendance")
        conn.execute("DROP TABLE IF EXISTS students")
        conn.commit()
        conn.close()
        init_db()
        print("Database deleted and reset.\n")
    else:
        print("Cancelled. Nothing was deleted.\n")


MENU = """
==========================================
   AI CLASS ATTENDANCE SYSTEM
==========================================
1. Add new entry to database
2. Show database
3. Scan a tag
4. Take attendance
5. Attendance list
6. Delete the database
7. Exit
==========================================
"""


def main():
    init_db()
    actions = {
        "1": add_entry,
        "2": show_database,
        "3": scan_tag,
        "4": take_attendance,
        "5": attendance_list,
        "6": delete_database,
    }
    while True:
        print(MENU)
        choice = input("Choose an option (1-7) > ").strip()
        if choice == "7":
            print("Goodbye!")
            sys.exit(0)
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid option. Please choose 1-7.\n")


if __name__ == "__main__":
    main()
