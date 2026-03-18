"""
╔══════════════════════════════════════════════════════════════╗
║  setup_database.py                                           ║
║  What this file does:                                        ║
║    Creates a file called  attendance.db                      ║
║    That file IS the database — it stores all your data.      ║
║    Think of it like an Excel workbook with 3 sheets.         ║
║                                                              ║
║  NOTE: You do NOT need to run this manually.                 ║
║        START_HERE.py runs it for you automatically.          ║
║                                                              ║
║  But if you want to run it alone:  python setup_database.py  ║
╚══════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT IS A DATABASE?
  A database is just a file that stores data in organized tables.
  Like Excel but more powerful.
  Our database has 3 tables (like 3 spreadsheet sheets):

    Sheet 1 = students       → who the students are
    Sheet 2 = rfid_tags      → which bracelet belongs to which student
    Sheet 3 = scan_events    → every scan that ever happened (the log)

WHY 3 SEPARATE TABLES?
  Imagine writing the student's full name on every attendance row.
  If they change their name, you'd have to fix 1000 rows.
  Instead:
    • We write the name ONCE in the students table.
    • Every other table just stores the ID (like "STU001").
    • This is called "normalization" — it keeps data clean and efficient.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# These are tools that come built into Python — no installation needed.
# ─────────────────────────────────────────────────────────────────────────────
import sqlite3   # sqlite3 = the tool that creates and reads .db files
import os        # os = operating system tools (like checking if a file exists)

# This is the name of the database file that will be created in this folder.
DB_NAME = "attendance.db"


def create_database():
    """
    This function creates the database file and the 3 tables inside it.
    A "function" is a block of code with a name — we call it to run it.
    """

    # ── Connect to (or create) the database file ──────────────────────────────
    # sqlite3.connect() means: "open this file, create it if it doesn't exist"
    # The result is called a "connection" — our open channel to the database.
    connection = sqlite3.connect(DB_NAME)

    # A "cursor" is like a pen that writes SQL commands into the database.
    # Think of the connection as the door, and the cursor as the hand that writes.
    cursor = connection.cursor()

    # ─────────────────────────────────────────────────────────────────────────
    # TABLE 1: students
    #
    # Stores one row per student.
    # student_id is the PRIMARY KEY — it must be unique (no two students
    # can have the same ID). It's like a student number badge.
    # ─────────────────────────────────────────────────────────────────────────
    print("Creating table: students ...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (

            student_id  TEXT PRIMARY KEY,
            --          ^^^^           ↑
            --          data type      this means every student_id must be unique
            --          TEXT = letters/numbers

            full_name   TEXT NOT NULL,
            --               ↑
            --               NOT NULL means this field cannot be empty

            department  TEXT NOT NULL,
            section     TEXT NOT NULL
        )
    """)
    # "IF NOT EXISTS" = only create if it doesn't exist yet (safe to re-run)

    # ─────────────────────────────────────────────────────────────────────────
    # TABLE 2: rfid_tags
    #
    # Stores one row per physical RFID bracelet.
    # Links each bracelet to a student via student_id (FOREIGN KEY).
    # uid = the code the USB reader types when a bracelet is scanned.
    # ─────────────────────────────────────────────────────────────────────────
    print("Creating table: rfid_tags ...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rfid_tags (

            tag_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            --                                ↑
            --                                AUTOINCREMENT = SQLite picks the
            --                                number automatically (1, 2, 3...)

            student_id  TEXT NOT NULL UNIQUE,
            --                        ↑
            --                        UNIQUE = one bracelet per student only

            uid         TEXT NOT NULL UNIQUE,
            --          the code the RFID reader types (e.g. "A1B2C3D4")
            --          also UNIQUE — each bracelet has a different code

            label       TEXT,
            --          optional name like "B001" to identify the bracelet

            created_at  TEXT DEFAULT (datetime('now')),
            --                        ↑
            --                        automatically saves the date/time registered

            FOREIGN KEY (student_id) REFERENCES students(student_id)
            --  ↑
            --  This LINE is the CONNECTION between rfid_tags and students.
            --  It says: "student_id here must exist in the students table."
            --  This prevents registering a bracelet for a non-existent student.
        )
    """)

    # ─────────────────────────────────────────────────────────────────────────
    # TABLE 3: scan_events
    #
    # Every time a bracelet is scanned, one new row is added here.
    # This IS your attendance log.
    # ─────────────────────────────────────────────────────────────────────────
    print("Creating table: scan_events ...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_events (

            scan_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            --          just an auto-numbered row ID

            tag_id      INTEGER NOT NULL,
            --          which bracelet was scanned (links to rfid_tags)

            scanned_at  TEXT DEFAULT (datetime('now')),
            --          the exact date and time of the scan — automatic!

            FOREIGN KEY (tag_id) REFERENCES rfid_tags(tag_id)
            --  Links this scan back to the bracelet that was scanned.
        )
    """)

    # ── Save and close ────────────────────────────────────────────────────────
    # commit() = "officially save everything I just wrote"
    # Without this, the changes are only in memory — not saved to the file.
    connection.commit()

    # close() = "close the door to the database"
    # Always close when you're done — good habit.
    connection.close()

    print(f"\n✔ Database '{DB_NAME}' created successfully!")
    print("  Tables ready: students, rfid_tags, scan_events")
    print("\nNext step: run  python seed_data.py")


# ─────────────────────────────────────────────────────────────────────────────
# THIS BLOCK runs when you type: python setup_database.py
# The condition  __name__ == "__main__"  is True only when the file is run
# directly. When imported by another file (like START_HERE.py), it is False.
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if os.path.exists(DB_NAME):
        print(f"Note: '{DB_NAME}' already exists — tables won't be overwritten.")
    create_database()
