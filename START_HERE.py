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
    On every run after that, this function does nothing (IF NOT EXISTS).
    """
    conn = sqlite3.connect(DB_FILE)
    # sqlite3.connect() opens the file. If the file doesn't exist yet,
    # SQLite creates an empty one automatically.

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
# MAIN MENU
# Shows 2 options in a loop. Keeps running until the user types 0 to exit.
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
  │  0  →  Exit                              │
  └──────────────────────────────────────────┘""")

        choice = input("\n  Choose 1, 2, or 0: ").strip()

        if choice == "1":
            add_new_entry()

        elif choice == "2":
            scan_tag()

        elif choice == "0":
            print("\n  Goodbye! Your data is saved in attendance.db\n")
            break
            # break = stop the while loop and end the program

        else:
            print("\n  Please type 1, 2, or 0.\n")


# ─────────────────────────────────────────────────────────────────────────────
# This is the entry point.
# When you type  python START_HERE.py  this is the first thing that runs.
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
