"""
╔══════════════════════════════════════════════════════════════╗
║  seed_data.py                                                ║
║  What this file does:                                        ║
║    Adds 5 fake students and 5 fake RFID tags into the        ║
║    database so you can test the system immediately           ║
║    without needing real hardware first.                      ║
║                                                              ║
║  NOTE: START_HERE.py runs this automatically.                ║
║  Manual run:  python seed_data.py                            ║
╚══════════════════════════════════════════════════════════════╝

"Seeding" a database means filling it with starter/sample data.
Like planting seeds before harvest — you put data in so you can
test your code, then replace it with real data later.
"""

import sqlite3   # the tool that talks to our .db file

DB_NAME = "attendance.db"   # the database file we target


def seed():
    """
    Inserts sample students and RFID tags into the database.
    Running this twice is safe — duplicates are skipped automatically.
    """

    # Open the database file (it must already exist — run setup_database.py first)
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    # ─────────────────────────────────────────────────────────────────────────
    # SAMPLE STUDENTS
    #
    # Each entry is a "tuple" — a group of values inside ( )
    # The order matches the table columns:
    #   (student_id, full_name, department, section)
    # ─────────────────────────────────────────────────────────────────────────
    students = [
        ("STU001", "Alice Reyes",    "Computer Science",       "3A"),
        ("STU002", "Ben Santos",     "Information Technology", "3B"),
        ("STU003", "Clara Mendoza",  "Computer Science",       "3A"),
        ("STU004", "David Cruz",     "Electronics",            "2C"),
        ("STU005", "Eva Lim",        "Information Technology", "2A"),
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # SAMPLE RFID TAGS
    #
    # uid = the code the USB reader would type for that bracelet
    # label = a human-friendly name for the bracelet
    # Order: (student_id, uid, label)
    # ─────────────────────────────────────────────────────────────────────────
    rfid_tags = [
        ("STU001", "A1B2C3D4", "B001"),   # Alice's bracelet
        ("STU002", "E5F6A7B8", "B002"),   # Ben's bracelet
        ("STU003", "C9D0E1F2", "B003"),   # Clara's bracelet
        ("STU004", "G3H4I5J6", "B004"),   # David's bracelet
        ("STU005", "K7L8M9N0", "B005"),   # Eva's bracelet
    ]

    # ── Insert students ───────────────────────────────────────────────────────
    print("Inserting sample students ...")

    # "for s in students" means: go through each student one by one
    # s will be  ("STU001", "Alice Reyes", ...)  on the first loop,
    # then       ("STU002", "Ben Santos",  ...)  on the second, etc.
    for s in students:
        try:
            # The ? marks are placeholders — Python fills them in from the tuple.
            # This is safer than writing the values directly into the SQL string.
            cursor.execute("""
                INSERT INTO students (student_id, full_name, department, section)
                VALUES (?, ?, ?, ?)
            """, s)
            print(f"  ✔ Added: {s[1]} ({s[0]})")
            #           ^^^^       ^^^
            #           s[1] = second item in the tuple = full_name
            #           s[0] = first item = student_id

        except sqlite3.IntegrityError:
            # IntegrityError happens when we try to insert a student_id that
            # already exists (remember student_id is UNIQUE / PRIMARY KEY).
            # We just skip it instead of crashing.
            print(f"  – Skipped (already exists): {s[1]}")

    # ── Insert RFID tags ──────────────────────────────────────────────────────
    print("\nInserting sample RFID tags ...")

    for t in rfid_tags:
        try:
            cursor.execute("""
                INSERT INTO rfid_tags (student_id, uid, label)
                VALUES (?, ?, ?)
            """, t)
            print(f"  ✔ Tag {t[2]} → Student {t[0]}  (UID: {t[1]})")

        except sqlite3.IntegrityError:
            print(f"  – Skipped (already exists): UID {t[1]}")

    # Save all changes to disk
    connection.commit()
    connection.close()

    print("\n✔ Sample data is ready!")
    print("\nTest UIDs (type these in the scanner to see them work):")
    print("  A1B2C3D4  →  Alice Reyes")
    print("  E5F6A7B8  →  Ben Santos")
    print("  C9D0E1F2  →  Clara Mendoza")
    print("  G3H4I5J6  →  David Cruz")
    print("  K7L8M9N0  →  Eva Lim")


# Runs only when you execute  python seed_data.py  directly
if __name__ == "__main__":
    seed()
