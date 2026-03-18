"""
register_tag.py
---------------
PART 5 — RFID REGISTRATION PROGRAM

This script links an RFID wristband (UID) to a student record.

Steps:
  1. Ask for the student's ID (e.g. STU001).
  2. Confirm the student exists.
  3. Wait for the RFID reader to type a UID (scan the bracelet).
  4. Ask for a bracelet label (e.g. B006) — optional but helpful.
  5. Save the link in the rfid_tags table.
  6. Prevent duplicate assignments (one tag per student; unique UIDs).

Usage:
    python register_tag.py
"""

import sqlite3

DB_NAME = "attendance.db"


def find_student(cursor, student_id):
    """Returns student row or None."""
    cursor.execute("""
        SELECT student_id, full_name, department, section
        FROM students
        WHERE student_id = ?
    """, (student_id,))
    return cursor.fetchone()


def uid_already_registered(cursor, uid):
    """Returns True if this UID is already in the database."""
    cursor.execute("SELECT tag_id FROM rfid_tags WHERE uid = ?", (uid,))
    return cursor.fetchone() is not None


def student_already_has_tag(cursor, student_id):
    """Returns True if this student already has a tag assigned."""
    cursor.execute("SELECT tag_id FROM rfid_tags WHERE student_id = ?", (student_id,))
    return cursor.fetchone() is not None


def register(cursor, connection):
    """Runs one registration workflow."""

    print("\n" + "=" * 50)
    print("  RFID TAG REGISTRATION")
    print("=" * 50)

    # ── Step 1: Get student ID ───────────────────
    student_id = input("Enter student ID (e.g. STU001): ").strip().upper()
    if not student_id:
        print("No student ID entered. Cancelled.")
        return

    # ── Step 2: Confirm student exists ──────────
    student = find_student(cursor, student_id)
    if student is None:
        print(f"  ✘ Student '{student_id}' not found in the database.")
        print("    Check the ID or add the student first.")
        return

    print(f"\n  Found: {student[1]} | {student[2]} | Section {student[3]}")

    # ── Check if student already has a tag ──────
    if student_already_has_tag(cursor, student_id):
        print(f"  ✘ This student already has an RFID tag assigned.")
        print("    Remove the old tag from rfid_tags first if you want to replace it.")
        return

    # ── Step 3: Scan the RFID bracelet ──────────
    print("\nNow SCAN the bracelet near the reader (it will type the UID automatically).")
    uid = input("UID (auto-typed by reader): ").strip()

    if not uid:
        print("  ✘ No UID received. Cancelled.")
        return

    # ── Prevent duplicate UID ───────────────────
    if uid_already_registered(cursor, uid):
        print(f"  ✘ UID '{uid}' is already assigned to another student.")
        print("    Each bracelet can only be linked to one student.")
        return

    # ── Step 4: Bracelet label (optional) ───────
    label = input("Enter bracelet label (e.g. B006), or press Enter to skip: ").strip()
    if not label:
        label = None   # Store NULL in the database if no label given.

    # ── Step 5: Save to database ─────────────────
    cursor.execute("""
        INSERT INTO rfid_tags (student_id, uid, label)
        VALUES (?, ?, ?)
    """, (student_id, uid, label))
    connection.commit()

    print("\n  ✔ Tag registered successfully!")
    print(f"    Student  : {student[1]} ({student_id})")
    print(f"    UID      : {uid}")
    print(f"    Label    : {label if label else '(none)'}")


def main():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    while True:
        register(cursor, connection)

        print()
        again = input("Register another tag? (y/n): ").strip().lower()
        if again != "y":
            break

    connection.close()
    print("\nDone. You can now scan registered bracelets with:")
    print("  python scan_lookup.py")
    print("  python app.py")


if __name__ == "__main__":
    main()
