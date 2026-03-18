"""
seed_data.py
------------
This script inserts sample students and RFID tags into the database
so you can test the system without real hardware right away.

Run this AFTER setup_database.py.

Usage:
    python seed_data.py
"""

import sqlite3

DB_NAME = "attendance.db"


def seed():
    """Inserts sample students and RFID tags."""

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    # ─────────────────────────────────────────────
    # PART 2 — SAMPLE INSERT STATEMENTS
    # ─────────────────────────────────────────────

    # 5 sample students
    # (student_id, full_name, department, section)
    students = [
        ("STU001", "Alice Reyes",    "Computer Science",    "3A"),
        ("STU002", "Ben Santos",     "Information Technology", "3B"),
        ("STU003", "Clara Mendoza",  "Computer Science",    "3A"),
        ("STU004", "David Cruz",     "Electronics",         "2C"),
        ("STU005", "Eva Lim",        "Information Technology", "2A"),
    ]

    # 5 sample RFID tags — each uid simulates what the USB reader types.
    # (student_id, uid, label)
    rfid_tags = [
        ("STU001", "A1B2C3D4", "B001"),
        ("STU002", "E5F6A7B8", "B002"),
        ("STU003", "C9D0E1F2", "B003"),
        ("STU004", "G3H4I5J6", "B004"),
        ("STU005", "K7L8M9N0", "B005"),
    ]

    # ── Insert students ──────────────────────────
    print("Inserting sample students ...")
    for student in students:
        try:
            cursor.execute("""
                INSERT INTO students (student_id, full_name, department, section)
                VALUES (?, ?, ?, ?)
            """, student)
            print(f"  Added: {student[1]} ({student[0]})")
        except sqlite3.IntegrityError:
            # This error happens if the student_id already exists (UNIQUE constraint).
            print(f"  Skipped (already exists): {student[1]} ({student[0]})")

    # ── Insert RFID tags ─────────────────────────
    print("\nInsert sample RFID tags ...")
    for tag in rfid_tags:
        try:
            cursor.execute("""
                INSERT INTO rfid_tags (student_id, uid, label)
                VALUES (?, ?, ?)
            """, tag)
            print(f"  Tag {tag[2]} → Student {tag[0]}  UID: {tag[1]}")
        except sqlite3.IntegrityError:
            print(f"  Skipped (already exists): UID {tag[1]}")

    connection.commit()
    connection.close()

    print("\nSample data inserted successfully!")
    print("\nYou can now test by running:")
    print("  python scan_lookup.py")
    print("  python register_tag.py")
    print("  python app.py")
    print("\nTest UIDs to try: A1B2C3D4 / E5F6A7B8 / C9D0E1F2 / G3H4I5J6 / K7L8M9N0")


if __name__ == "__main__":
    seed()
