"""
╔══════════════════════════════════════════════════════════════╗
║           📡  RFID STUDENT ATTENDANCE SYSTEM                 ║
╠══════════════════════════════════════════════════════════════╣
║  HOW TO RUN:   python START_HERE.py                          ║
║                                                              ║
║  OPTION 1 → Add a new student + assign their bracelet        ║
║  OPTION 2 → Scan a bracelet to see who it belongs to         ║
║                                                              ║
║  Your data is saved in  attendance.db                        ║
║  That file stays on your computer — nothing is lost          ║
║  when you close and reopen the program.                      ║
╚══════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────────────────────────────────────
# sqlite3 is a Python built-in tool for creating and reading database files.
# No installation needed — it comes with Python.
# os is another built-in tool for checking if files exist on your computer.
# ─────────────────────────────────────────────────────────────────────────────
import sqlite3
import os

# ─────────────────────────────────────────────────────────────────────────────
# DB_FILE is the name of the database file.
# SQLite saves everything into ONE file (attendance.db) in the same folder.
# The file is created once and keeps growing as you add more students.
# Closing the program does NOT delete it — your data is safe.
# ─────────────────────────────────────────────────────────────────────────────
DB_FILE = "attendance.db"


# ═════════════════════════════════════════════════════════════════════════════
# DATABASE SETUP
# Creates the database and the students table if they don't exist yet.
# If attendance.db already exists (from a previous run), nothing is changed.
# ═════════════════════════════════════════════════════════════════════════════

def setup_database():
    """
    Creates attendance.db and the students table on first run only.
    Also detects and upgrades old database layouts from previous versions.
    """
    conn = sqlite3.connect(DB_FILE)

    # ── Check if the table already exists and what columns it has ─────────
    # PRAGMA table_info() is a SQLite command that lists all columns
    # in a table. We use it to detect old incompatible database layouts.
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(students)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    # existing_columns will be something like ['student_id', 'full_name', ...]
    # or [] if the table doesn't exist yet.

    # ── If the table exists but uses the OLD column layout, drop it ───────
    # The old layout used 'full_name' and 'student_id'.
    # The new layout uses 'name', 'fun_fact', 'uid'.
    # If we find old columns, we delete the old table so the new one can
    # be created cleanly below.
    if existing_columns and "name" not in existing_columns:
        print()
        print("  ┌─────────────────────────────────────────────────────┐")
        print("  │  NOTE: Old database format detected.                │")
        print("  │  The table layout changed in this version.          │")
        print("  │  The old table has been replaced automatically.     │")
        print("  │  Please re-add your students using Option 1.        │")
        print("  └─────────────────────────────────────────────────────┘")
        conn.execute("DROP TABLE students")
        conn.commit()

    # ── Create the table (skipped if it already exists with correct layout)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (

            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            -- id is a row number SQLite assigns automatically: 1, 2, 3...
            -- You never type this yourself.

            name        TEXT NOT NULL,
            -- The student's full name. NOT NULL means it can't be empty.

            department  TEXT NOT NULL,
            -- e.g. "Computer Science"

            fun_fact    TEXT,
            -- Something interesting about the student. Optional.

            uid         TEXT UNIQUE NOT NULL,
            -- The code the RFID reader types when the bracelet is scanned.
            -- UNIQUE means no two students can have the same bracelet.

            added_at    TEXT DEFAULT CURRENT_TIMESTAMP
            -- The date and time this entry was created. Fills in automatically.
        )
    """)

    conn.commit()   # commit = "save everything to the file"
    conn.close()    # close = "done using the database for now"


# ═════════════════════════════════════════════════════════════════════════════
# OPTION 1 — ADD NEW ENTRY TO DATABASE
#
# Asks for student info, then asks to scan a bracelet to link it.
# All information is saved permanently to attendance.db.
# ═════════════════════════════════════════════════════════════════════════════

def add_new_entry():
    print()
    print("┌─────────────────────────────────────────────────┐")
    print("│  ADD NEW STUDENT                                │")
    print("└─────────────────────────────────────────────────┘")
    print()

    # ── Ask for the student's name ─────────────────────────────────────────
    name = input("  Student name: ").strip()
    # .strip() removes any extra spaces the user accidentally typed

    if not name:
        # If the user just pressed Enter without typing anything, cancel.
        print("\n  Nothing entered. Going back to menu.\n")
        return

    # ── Ask for the department ─────────────────────────────────────────────
    department = input("  Department  : ").strip()

    if not department:
        print("\n  Nothing entered. Going back to menu.\n")
        return

    # ── Ask for a fun fact ─────────────────────────────────────────────────
    fun_fact = input("  Fun fact    : ").strip()

    if not fun_fact:
        fun_fact = "(none provided)"
        # If they skip the fun fact, we store a placeholder instead of blank.

    # ── Scan the bracelet ──────────────────────────────────────────────────
    print()
    print("  ─────────────────────────────────────────────────")
    print(f"  Almost done! Now assign a bracelet to {name}.")
    print("  Hold the bracelet near the USB reader.")
    print("  It will type the UID automatically and press Enter.")
    print("  ─────────────────────────────────────────────────")
    print()

    uid = input("  Scan bracelet ▶ ").strip()

    if not uid:
        print("\n  No bracelet scanned. Going back to menu.\n")
        return

    # ── Save everything to the database ───────────────────────────────────
    conn = sqlite3.connect(DB_FILE)

    try:
        conn.execute("""
            INSERT INTO students (name, department, fun_fact, uid)
            VALUES (?, ?, ?, ?)
        """, (name, department, fun_fact, uid))
        # The ? marks are safe placeholders — Python fills them in.
        # Never put variables directly inside the SQL string (security risk).

        conn.commit()   # save to file

        print()
        print("  ✔ ─────────────────────────────────────────────")
        print(f"  ✔  Entry saved successfully!")
        print(f"  ✔  Name       : {name}")
        print(f"  ✔  Department : {department}")
        print(f"  ✔  Fun Fact   : {fun_fact}")
        print(f"  ✔  Bracelet   : {uid}")
        print("  ✔ ─────────────────────────────────────────────")
        print()

    except sqlite3.IntegrityError:
        # This error fires when the uid already exists in the database.
        # Remember: uid has UNIQUE on it — one bracelet per person.
        print()
        print("  ✘ That bracelet is already assigned to someone else.")
        print("  ✘ Each bracelet can only belong to one student.")
        print("     Try scanning a different bracelet.")
        print()

    except sqlite3.OperationalError:
        # This error means the database has an old layout from a previous
        # version of this program (different column names).
        # Fix: drop the old table, create the correct one, retry the insert.
        print()
        print("  Detected old database layout — rebuilding table...")
        conn.execute("DROP TABLE IF EXISTS students")
        conn.execute("""
            CREATE TABLE students (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                department TEXT NOT NULL,
                fun_fact   TEXT,
                uid        TEXT UNIQUE NOT NULL,
                added_at   TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        # Retry the insert now that the table is correct
        try:
            conn.execute("""
                INSERT INTO students (name, department, fun_fact, uid)
                VALUES (?, ?, ?, ?)
            """, (name, department, fun_fact, uid))
            conn.commit()
            print()
            print("  ✔ ─────────────────────────────────────────────")
            print(f"  ✔  Database fixed and entry saved!")
            print(f"  ✔  Name       : {name}")
            print(f"  ✔  Department : {department}")
            print(f"  ✔  Fun Fact   : {fun_fact}")
            print(f"  ✔  Bracelet   : {uid}")
            print("  ✔ ─────────────────────────────────────────────")
            print()
        except Exception as retry_err:
            print(f"  ✘ Could not save: {retry_err}")
            print()

    conn.close()


# ═════════════════════════════════════════════════════════════════════════════
# OPTION 2 — SCAN A TAG
#
# Waits for a bracelet scan, then shows the matching student info.
# If the bracelet isn't in the database, says so clearly.
# ═════════════════════════════════════════════════════════════════════════════

def scan_tag():
    print()
    print("┌─────────────────────────────────────────────────┐")
    print("│  SCAN A TAG                                     │")
    print("└─────────────────────────────────────────────────┘")
    print()
    print("  Hold the bracelet near the reader.")
    print("  (Or type a UID manually and press Enter to test.)")
    print()

    uid = input("  Scan bracelet ▶ ").strip()

    if not uid:
        print("\n  Nothing scanned. Going back to menu.\n")
        return

    # ── Look up the UID in the database ────────────────────────────────────
    conn = sqlite3.connect(DB_FILE)

    row = conn.execute("""
        SELECT name, department, fun_fact, added_at
        FROM students
        WHERE uid = ?
    """, (uid,)).fetchone()
    # fetchone() returns one result row, or None if nothing matched.

    conn.close()

    print()

    if row:
        # ── Found! Display the student card ───────────────────────────────
        # row[0] = name, row[1] = department, row[2] = fun_fact, row[3] = added_at
        print("  ╔═════════════════════════════════════════════╗")
        print("  ║  ✔  TAG RECOGNIZED                         ║")
        print("  ╠═════════════════════════════════════════════╣")
        print(f"  ║  Name       :  {row[0]:<28} ║")
        print(f"  ║  Department :  {row[1]:<28} ║")
        print(f"  ║  Fun Fact   :  {row[2]:<28} ║")
        print(f"  ║  Added on   :  {row[3]:<28} ║")
        print("  ╚═════════════════════════════════════════════╝")

    else:
        # ── Not found ──────────────────────────────────────────────────────
        print("  ✘ ─────────────────────────────────────────────")
        print(f"  ✘  Tag not found in database.")
        print(f"  ✘  UID scanned: {uid}")
        print()
        print("     This bracelet has not been registered yet.")
        print("     Go back to the menu and choose:")
        print("     Option 1 → Add New Entry to Database")
        print("  ✘ ─────────────────────────────────────────────")

    print()


# ═════════════════════════════════════════════════════════════════════════════
# OPTION 3 — SHOW ALL STUDENTS IN THE DATABASE
#
# Prints every student as a card so you can see all stored info at a glance.
# ═════════════════════════════════════════════════════════════════════════════

def show_database():
    print()
    print("┌─────────────────────────────────────────────────┐")
    print("│  ALL STUDENTS IN DATABASE                       │")
    print("└─────────────────────────────────────────────────┘")

    conn = sqlite3.connect(DB_FILE)

    # SELECT * means "give me every column".
    # ORDER BY id means show them in the order they were added (oldest first).
    rows = conn.execute("""
        SELECT id, name, department, fun_fact, uid, added_at
        FROM students
        ORDER BY id
    """).fetchall()
    # fetchall() returns every matching row as a list.
    # If the table is empty, it returns an empty list [].

    conn.close()

    if not rows:
        print()
        print("  No students yet. Use Option 1 to add the first one.")
        print()
        return

    # Print one card per student
    for row in rows:
        # row[0]=id  row[1]=name  row[2]=department
        # row[3]=fun_fact  row[4]=uid  row[5]=added_at
        print()
        print(f"  ┌─── Student #{row[0]} ───────────────────────────────┐")
        print(f"  │  Name       :  {row[1]:<30} │")
        print(f"  │  Department :  {row[2]:<30} │")
        print(f"  │  Fun Fact   :  {row[3]:<30} │")
        print(f"  │  Bracelet   :  {row[4]:<30} │")
        print(f"  │  Added on   :  {row[5]:<30} │")
        print(f"  └────────────────────────────────────────────────┘")

    print()
    print(f"  Total: {len(rows)} student(s) in the database.")
    print()


# ═════════════════════════════════════════════════════════════════════════════
# OPTION 4 — ATTENDANCE LIST
#
# Starts a class attendance session.
# Students scan their bracelets one by one as they enter.
# Each scan adds them to a numbered list shown on screen.
# Duplicate scans are ignored (same student scanning twice).
# Type "done" when everyone has scanned to see the final list.
# ═════════════════════════════════════════════════════════════════════════════

def attendance_list():
    from datetime import datetime

    print()
    print("┌─────────────────────────────────────────────────┐")
    print("│  ATTENDANCE SESSION                             │")
    print("└─────────────────────────────────────────────────┘")
    print()
    print("  Ask each student to scan their bracelet.")
    print('  Type  done  when finished.')
    print()

    # present is a list that grows as students scan in.
    # We also keep a set of seen UIDs to prevent duplicates.
    present   = []    # stores names in order: ["Alice Reyes", "Ben Santos", ...]
    seen_uids = set() # stores UIDs already scanned so no one is counted twice

    conn = sqlite3.connect(DB_FILE)

    while True:
        try:
            uid = input("  Scan bracelet ▶ ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        # ── End the session ────────────────────────────────────────────────
        if uid.lower() == "done":
            break

        if not uid:
            continue   # ignore accidental Enter presses

        # ── Ignore if this bracelet was already scanned today ──────────────
        if uid in seen_uids:
            # Look up the name so the message is personal
            row = conn.execute(
                "SELECT name FROM students WHERE uid = ?", (uid,)
            ).fetchone()
            already = row[0] if row else uid
            print(f"  (already marked present: {already})")
            print()
            continue

        # ── Look up the student ────────────────────────────────────────────
        row = conn.execute(
            "SELECT name, department FROM students WHERE uid = ?", (uid,)
        ).fetchone()

        if row:
            # Add to the present list and remember this UID
            present.append(row[0])
            seen_uids.add(uid)

            number = len(present)   # their position in the list
            print(f"  {number}. {row[0]}  ({row[1]})")
            print()
        else:
            print(f"  ✘ Unknown tag — not in the database.")
            print()

    conn.close()

    # ── Print the final attendance list ───────────────────────────────────
    print()
    print("  ════════════════════════════════════════════════")
    print(f"  ATTENDANCE  —  {datetime.now().strftime('%Y-%m-%d  %H:%M')}")
    print("  ════════════════════════════════════════════════")

    if not present:
        print("  No students were scanned.")
    else:
        for i, name in enumerate(present, start=1):
            # enumerate gives us (1, name), (2, name), ...
            print(f"  {i}.  {name}")
        print()
        print(f"  Total present: {len(present)} student(s)")

    print("  ════════════════════════════════════════════════")
    print()


# ═════════════════════════════════════════════════════════════════════════════
# MAIN MENU
# Shows 4 options in a loop. Keeps running until the user types 0 to exit.
# ═════════════════════════════════════════════════════════════════════════════

def main():

    # Set up the database file (only does real work on the very first run)
    setup_database()

    # Count how many students are already saved, just to show the user.
    conn = sqlite3.connect(DB_FILE)
    count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    conn.close()

    # ── The main loop ──────────────────────────────────────────────────────
    # "while True" = keep showing the menu until the user chooses to exit.
    while True:

        # Print the menu
        print("""
╔══════════════════════════════════════════════╗
║       📡  RFID STUDENT ATTENDANCE SYSTEM    ║
╚══════════════════════════════════════════════╝""")

        # Show how many students are in the database right now
        conn = sqlite3.connect(DB_FILE)
        count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        conn.close()

        if count == 0:
            print("  Database is empty — no students added yet.")
        elif count == 1:
            print("  1 student in the database.")
        else:
            print(f"  {count} students in the database.")

        print("""
  ┌──────────────────────────────────────────┐
  │  1  →  Add New Entry to Database         │
  │  2  →  Scan a Tag                        │
  │  3  →  Show All Students                 │
  │  4  →  Attendance List                   │
  │  0  →  Exit                              │
  └──────────────────────────────────────────┘""")

        choice = input("\n  Choose 1, 2, 3, 4, or 0: ").strip()

        if choice == "1":
            add_new_entry()

        elif choice == "2":
            scan_tag()

        elif choice == "3":
            show_database()

        elif choice == "4":
            attendance_list()

        elif choice == "0":
            print("\n  Goodbye! Your data is saved in attendance.db\n")
            break
            # break = stop the while loop and end the program

        else:
            print("\n  Please type 1, 2, 3, 4, or 0.\n")


# ─────────────────────────────────────────────────────────────────────────────
# This is the entry point.
# When you type  python START_HERE.py  this is the first thing that runs.
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
