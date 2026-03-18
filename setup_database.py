"""
setup_database.py
-----------------
This script creates the SQLite database and all required tables
for the RFID Student Attendance System.

Run this FIRST before any other script.

Usage:
    python setup_database.py
"""

import sqlite3  # Built-in Python library — no installation needed
import os

# ─────────────────────────────────────────────
# DATABASE FILE NAME
# ─────────────────────────────────────────────
# The database will be saved as a single file in the same folder.
DB_NAME = "attendance.db"


def create_database():
    """Creates the database file and all tables."""

    # sqlite3.connect() creates the file if it doesn't exist yet.
    connection = sqlite3.connect(DB_NAME)

    # A cursor lets us send SQL commands to the database.
    cursor = connection.cursor()

    # ─────────────────────────────────────────────
    # PART 1 — DATABASE DESIGN (explained in comments)
    # ─────────────────────────────────────────────
    #
    # We use THREE separate tables (normalization):
    #
    # 1. students
    #    - Stores personal information about each student.
    #    - Primary key: student_id (TEXT, e.g. "STU001")
    #
    # 2. rfid_tags
    #    - Stores each physical RFID wristband/tag.
    #    - Primary key: tag_id (INTEGER, auto-assigned)
    #    - Foreign key: student_id → references students(student_id)
    #      One student can have one tag (one-to-one in this design).
    #    - uid: the unique code the reader types (e.g. "A1B2C3D4")
    #    - label: a human-readable bracelet name (e.g. "B001")
    #
    # 3. scan_events
    #    - Every time a tag is scanned, one row is added here.
    #    - Primary key: scan_id (INTEGER, auto-assigned)
    #    - Foreign key: tag_id → references rfid_tags(tag_id)
    #    - scanned_at: timestamp recorded automatically
    #
    # WHY SEPARATE TABLES?
    # - If a student's name changes, we update ONE row in 'students' —
    #   not hundreds of scan rows.
    # - If we want all scans for one student, we JOIN the tables.
    # - This avoids repeating the same data in many places (normalization).
    # ─────────────────────────────────────────────

    print("Creating table: students ...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id  TEXT PRIMARY KEY,   -- e.g. STU001 (must be unique)
            full_name   TEXT NOT NULL,      -- student's full name
            department  TEXT NOT NULL,      -- e.g. Computer Science
            section     TEXT NOT NULL       -- e.g. A, B, 3A, etc.
        )
    """)

    print("Creating table: rfid_tags ...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rfid_tags (
            tag_id      INTEGER PRIMARY KEY AUTOINCREMENT,  -- auto number
            student_id  TEXT NOT NULL UNIQUE,               -- one tag per student
            uid         TEXT NOT NULL UNIQUE,               -- the code the reader sends
            label       TEXT,                               -- e.g. B001 (optional)
            created_at  TEXT DEFAULT (datetime('now')),     -- when it was registered

            -- This line links rfid_tags back to the students table.
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)

    print("Creating table: scan_events ...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_events (
            scan_id     INTEGER PRIMARY KEY AUTOINCREMENT,  -- auto number
            tag_id      INTEGER NOT NULL,                   -- which tag was scanned
            scanned_at  TEXT DEFAULT (datetime('now')),     -- timestamp (automatic)
            notes       TEXT,                               -- optional extra info

            -- This links each scan back to the tag that was used.
            FOREIGN KEY (tag_id) REFERENCES rfid_tags(tag_id)
        )
    """)

    # Save the changes (always call commit after writing data).
    connection.commit()

    # Close the connection when done — good practice.
    connection.close()

    print(f"\nDatabase '{DB_NAME}' created successfully!")
    print("Tables created: students, rfid_tags, scan_events")
    print("\nNext step: run  python seed_data.py")


# ─────────────────────────────────────────────
# ENTRY POINT
# This block runs only when you execute this file directly.
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # Warn the user if the database already exists.
    if os.path.exists(DB_NAME):
        print(f"Note: '{DB_NAME}' already exists. Tables will NOT be overwritten.")
    create_database()
