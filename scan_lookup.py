"""
scan_lookup.py
--------------
PART 4 — RFID SCAN PROGRAM (TERMINAL)

This script runs in a loop and waits for the RFID reader to type a UID.
When a UID is received it:
  1. Looks up the student linked to that tag.
  2. Prints the student's ID, name, department, and section.
  3. Logs the scan into the scan_events table.
  4. Shows "Unknown tag" if the UID is not registered.

Type "exit" to quit.

HOW THE RFID READER WORKS:
  The USB RFID reader acts like a keyboard (HID device).
  When a bracelet is held near the reader it automatically
  types the tag's UID and presses Enter.
  Python's input() captures exactly that — it waits for Enter.

Usage:
    python scan_lookup.py
"""

import sqlite3
from datetime import datetime

DB_NAME = "attendance.db"


def get_student_by_uid(cursor, uid):
    """
    Looks up a student using the tag UID.
    Returns a dict with student info, or None if not found.

    The SQL JOIN connects three tables:
        rfid_tags  →  students
    so we can get the student name from just the UID.
    """
    cursor.execute("""
        SELECT
            s.student_id,
            s.full_name,
            s.department,
            s.section,
            t.tag_id,
            t.label
        FROM rfid_tags AS t
        -- JOIN links each tag row to its matching student row.
        JOIN students AS s ON t.student_id = s.student_id
        WHERE t.uid = ?
    """, (uid,))

    row = cursor.fetchone()   # Returns one row or None
    if row is None:
        return None

    # Turn the row into a readable dictionary.
    return {
        "student_id": row[0],
        "full_name":  row[1],
        "department": row[2],
        "section":    row[3],
        "tag_id":     row[4],
        "label":      row[5],
    }


def log_scan(cursor, tag_id):
    """
    Inserts a new row into scan_events for the given tag_id.
    SQLite fills in scanned_at automatically (see table definition).
    """
    cursor.execute("""
        INSERT INTO scan_events (tag_id)
        VALUES (?)
    """, (tag_id,))


def print_separator():
    print("─" * 50)


def main():
    # Open a single database connection for the whole session.
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    print("=" * 50)
    print("  RFID ATTENDANCE SCANNER — TERMINAL MODE")
    print("=" * 50)
    print("Scan a bracelet OR type a UID and press Enter.")
    print('Type "exit" to quit.\n')

    while True:
        try:
            # input() blocks here and waits for a line of text.
            # The RFID reader types the UID and presses Enter automatically.
            uid = input("Scan tag (or type UID): ").strip()
        except (EOFError, KeyboardInterrupt):
            # Ctrl+C or end-of-input exits gracefully.
            print("\nScanner stopped.")
            break

        # ── Handle exit command ──────────────────
        if uid.lower() == "exit":
            print("Goodbye!")
            break

        # ── Ignore empty input (accidental Enter) ─
        if not uid:
            continue

        print_separator()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  UID: {uid}")

        # ── Look up the student ──────────────────
        student = get_student_by_uid(cursor, uid)

        if student:
            # ── Known tag: print info and log ────
            print(f"  Student ID : {student['student_id']}")
            print(f"  Name       : {student['full_name']}")
            print(f"  Department : {student['department']}")
            print(f"  Section    : {student['section']}")
            print(f"  Bracelet   : {student['label']}")

            log_scan(cursor, student["tag_id"])
            connection.commit()   # Save the scan to disk immediately.
            print("  ✔ Attendance logged.")
        else:
            # ── Unknown tag ──────────────────────
            print("  ✘ Unknown tag — not registered in the system.")
            print("    Run  python register_tag.py  to register it.")

        print_separator()
        print()

    connection.close()


if __name__ == "__main__":
    main()
