"""
╔══════════════════════════════════════════════════════════════╗
║  register_tag.py                                             ║
║  What this file does:                                        ║
║    Connects a physical RFID bracelet to a student.           ║
║    You do this ONCE per bracelet before it can be used       ║
║    for attendance.                                           ║
║                                                              ║
║  NOTE: START_HERE.py → Option 2 runs this for you.          ║
║  Manual run:  python register_tag.py                         ║
╚══════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THE PROCESS (4 simple steps):
  Step 1 → Type the student's ID  (e.g. STU001)
  Step 2 → System checks that student exists
  Step 3 → Scan the bracelet (reader types the UID automatically)
  Step 4 → Optionally name the bracelet (e.g. B006)
  Done  → Bracelet is now linked to that student forever
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sqlite3

DB_NAME = "attendance.db"


def find_student(cursor, student_id):
    """
    Looks up a student by their ID.
    Returns their row if found, or None if not found.
    """
    cursor.execute("""
        SELECT student_id, full_name, department, section
        FROM students
        WHERE student_id = ?
    """, (student_id,))
    return cursor.fetchone()
    # fetchone() = get one result row, or None if nothing matched


def uid_taken(cursor, uid):
    """Returns True if this UID is already in the database."""
    cursor.execute("SELECT tag_id FROM rfid_tags WHERE uid = ?", (uid,))
    return cursor.fetchone() is not None
    # "is not None" = True if a row was found (meaning it exists)


def student_has_tag(cursor, student_id):
    """Returns True if this student already has a bracelet."""
    cursor.execute("SELECT tag_id FROM rfid_tags WHERE student_id = ?", (student_id,))
    return cursor.fetchone() is not None


def register_one(cursor, connection):
    """
    Runs through the registration steps for one bracelet.
    Returns True if successful, False if cancelled or failed.
    """

    print("\n" + "━" * 50)
    print("  REGISTER A NEW BRACELET")
    print("━" * 50)

    # ── STEP 1: Ask for student ID ─────────────────────────────────────────
    print()
    print("  STEP 1 of 4 — Enter the student ID")
    print("  (Look at the students list — IDs look like STU001)")
    print()
    student_id = input("  Student ID: ").strip().upper()
    # .upper() makes sure STU001 and stu001 both work

    if not student_id or student_id == "EXIT":
        print("  Cancelled.")
        return False

    # ── STEP 2: Confirm student exists ────────────────────────────────────
    student = find_student(cursor, student_id)

    if student is None:
        print(f"\n  ✘ No student found with ID '{student_id}'.")
        print("    Did you type it correctly? Check option 5 in the menu for the list.")
        return False

    print(f"\n  ✔ Found student:  {student[1]}")
    print(f"    Department:      {student[2]}")
    print(f"    Section:         {student[3]}")

    # Check if this student already has a bracelet
    if student_has_tag(cursor, student_id):
        print(f"\n  ✘ {student[1]} already has a bracelet registered.")
        print("    Each student can only have one bracelet at a time.")
        return False

    # ── STEP 3: Scan the bracelet ──────────────────────────────────────────
    print()
    print("  STEP 3 of 4 — Scan the bracelet")
    print("  Hold the bracelet near the USB reader.")
    print("  It will type the UID automatically and press Enter.")
    print()
    uid = input("  UID (scanned by reader): ").strip()

    if not uid:
        print("  ✘ Nothing received. Try again.")
        return False

    # Make sure this UID isn't already used by someone else
    if uid_taken(cursor, uid):
        print(f"  ✘ UID '{uid}' is already assigned to another student.")
        print("    Each bracelet has a unique code — this one is taken.")
        return False

    # ── STEP 4: Optional label ─────────────────────────────────────────────
    print()
    print("  STEP 4 of 4 — Give the bracelet a label (optional)")
    print("  A label is just a nickname like  B006  so you can identify it.")
    print("  Press Enter to skip this step.")
    print()
    label = input("  Bracelet label: ").strip()
    label = label if label else None
    # If label is empty string, store None (NULL) in the database

    # ── SAVE ───────────────────────────────────────────────────────────────
    cursor.execute("""
        INSERT INTO rfid_tags (student_id, uid, label)
        VALUES (?, ?, ?)
    """, (student_id, uid, label))
    connection.commit()

    print()
    print("  ✔ Bracelet registered successfully!")
    print(f"    Student   :  {student[1]}  ({student_id})")
    print(f"    UID       :  {uid}")
    print(f"    Label     :  {label or '(none)'}")
    print()
    print("  This bracelet will now be recognized by the scanner.")
    return True


def main():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    while True:
        register_one(cursor, connection)

        print()
        again = input("  Register another bracelet? (y / n): ").strip().lower()
        if again != "y":
            break

    connection.close()
    print("\n  Done! The bracelets are ready to use.")


# Runs only when executed directly: python register_tag.py
if __name__ == "__main__":
    main()
